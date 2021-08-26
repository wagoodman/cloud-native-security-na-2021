import json
import os
import logging
import logging.config
import tarfile
import shutil
import hashlib

from typing import Dict, Any, Tuple

import click


class OCIImageDir:

    def __init__(self, path: str):
        self.path = path

    def _path(self, *relative_path: str) -> str:
        return os.path.join(self.path, *relative_path)

    def blob_path(self, digest: str, algorithm: str = "sha256") -> str:
        algorithm, digest = parse_qualified_digest(digest, default_algorithm=algorithm)
        return self._path("blobs", algorithm, digest)

    def _write_contents(self, relative_path: str, contents: str, message: str = ""):
        image_path = self._path(relative_path)
        
        logging.debug(f"writing {message} to path={image_path!r}")
        
        with open(image_path, 'w') as f:
            f.write(contents)

    def _write_blob(self, contents: str, message: str = "blob") -> str:
        digest = string_digest(contents)
        image_path = self.blob_path(digest)

        if os.path.exists(image_path):
            # the contents already exist, ignore
            return digest

        logging.debug(f"writing {message} to path={image_path!r}")

        with open(image_path, 'w') as f:
            f.write(contents)

        return digest

    def delete_blob(self, digest: str, message: str = "blob"):
        image_path = self.blob_path(digest)
        if os.path.exists(image_path):
            logging.debug(f"deleting {message} from path={image_path!r}")
            os.remove(image_path)

        # note: this does NOT delete references in the manifest, index, and config

    def _read_contents(self, relative_path: str) -> str:
        image_path = self._path(relative_path)

        # logging.debug(f"reading path={image_path!r}")
        
        with open(image_path, 'r') as f:
            return f.read()

    def read_blob(self, digest: str) -> str:
        image_path = self.blob_path(digest)

        # logging.debug(f"reading blob={image_path!r}")

        with open(image_path, 'r') as f:
            return f.read()

    def write_blob(self, contents: str, replace_blob_digest: str = None, message: str = "blob") -> str:
        # write contents to new blob
        new_digest = self._write_blob(contents, message=message)

        replace_blob_digest = qualify_digest(replace_blob_digest)
        new_digest = qualify_digest(new_digest)

        if not replace_blob_digest or replace_blob_digest == new_digest:
            return new_digest

        self.delete_blob(replace_blob_digest, message=message)

        logging.debug(f"replacing blob {replace_blob_digest!r} ---> {new_digest!r}")

        self._replace_manifest(replace_blob_digest, new_digest)
        self._replace_docker_config_blob(replace_blob_digest, new_digest)

        self._replace_index(replace_blob_digest, new_digest)
        self._replace_oci_config_blob(replace_blob_digest, new_digest)

    def _replace_oci_config_blob(self, old_digest: str, new_digest: str):
        config, old_config_digest = self.oci_config()
        _, old_digest = parse_qualified_digest(old_digest)
        _, new_digest = parse_qualified_digest(new_digest)

        layers = []
        for layer in config["layers"]:
            if layer["digest"].endswith(old_digest):
                layer["digest"] = layer["digest"].replace(old_digest, new_digest, -1)
            layers.append(layer)

        config["layers"] = layers

        self.write_blob(json.dumps(config), old_config_digest, message="OCI config")

    def _replace_docker_config_blob(self, old_digest: str, new_digest: str):
        config, old_config_digest = self.docker_config()
        _, old_digest = parse_qualified_digest(old_digest)
        _, new_digest = parse_qualified_digest(new_digest)

        layers = []
        for layer in config["rootfs"]["diff_ids"]:
            if layer.endswith(old_digest):
                layer = layer.replace(old_digest, new_digest, -1)
            layers.append(layer)

        config["rootfs"]["diff_ids"] = layers

        self.write_blob(json.dumps(config), old_config_digest, message="docker config")

    def _replace_index(self, old_digest: str, new_digest: str):
        index = self.index()
        _, old_digest = parse_qualified_digest(old_digest)
        _, new_digest = parse_qualified_digest(new_digest)

        for manifest in index["manifests"]:
            if manifest["digest"].endswith(old_digest):
                manifest["digest"] = manifest["digest"].replace(old_digest, new_digest, -1)

            # for simplicity let's just assume there are only blobs for a single image
            manifest["size"] = self._blob_size_sum()

        self._write_contents("index.json", json.dumps(index), message="index")

    def _blob_size_sum(self) -> int:
        # for simplicity, let's assume that there are only blobs for the current image (and there is only one manifest)
        return get_directory_size(self._path("blob"))

    def _replace_manifest(self, old_digest: str, new_digest: str):
        manifest = self.manifest()
        _, old_digest = parse_qualified_digest(old_digest)
        _, new_digest = parse_qualified_digest(new_digest)

        if manifest["Config"].endswith(old_digest):
            manifest["Config"] = manifest["Config"].replace(old_digest, new_digest, -1)

        layers = []
        for layer in manifest["Layers"]:
            if layer.endswith(old_digest):
                layer = layer.replace(old_digest, new_digest, -1)
            layers.append(layer)
        
        manifest["Layers"] = layers

        self._write_contents("manifest.json", json.dumps([manifest]), message="manifest")

    def index(self) -> Dict[str, Any]:
        return json.loads(self._read_contents("index.json"))

    def manifest(self) -> Dict[str, Any]:
        return json.loads(self._read_contents("manifest.json"))[0]

    def docker_config(self) -> Tuple[Dict[str, Any], str]:
        config_path = self.manifest()["Config"]
        digest = os.path.basename(config_path)
        return json.loads(self._read_contents(config_path)), digest

    def write_docker_config(self, obj: Dict[str, Any]):
        _, original_digest = self.docker_config()
        self.write_blob(json.dumps(obj), original_digest, message="docker config")

    def oci_config(self) -> Tuple[Dict[str, Any], str]:
        digest = self.index()["manifests"][0]["digest"]
        return json.loads(self.read_blob(digest)), digest

    def write_oci_config(self, obj: Dict[str, Any]):
        _, original_digest = self.oci_config()
        self.write_blob(json.dumps(obj), original_digest, message="OCI config")

    def layer_blob_digest(self, layer: int):
        config, _ = self.oci_config()
        return config["layers"][layer]["digest"]


def get_directory_size(start_path: str):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size


def string_digest(value: str) -> str:
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def parse_qualified_digest(value: str, default_algorithm: str = "sha256") -> Tuple[str, str]:
    fields = value.split(":")
    if len(fields) == 2:
        return fields[0], fields[1]
    return default_algorithm, value


def qualify_digest(value: str, default_algorithm: str = "sha256") -> str:
    algorithm, value = parse_qualified_digest(value, default_algorithm=default_algorithm)
    return f"{algorithm}:{value}"


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
    # TODO: the r:gz could be inferred from OCI media types instead of hard coding
    with tarfile.open(layer_tar, "r:gz") as tar:
        tar.extractall(path=to)


def write_new_config_history(image: OCIImageDir, layer: int):
    docker_config, _ = image.docker_config()
    docker_config["history"][layer]["created_by"] = "RUN /bin/sh -c rm /somewhere/nothing.txt # buildkit"
    image.write_docker_config(docker_config)


@click.group()
def cli():
    pass

@cli.command()
@click.option("--dir", required=True, help="directory with the untar'd container image (from a docker save command)")
@click.option("--layer", required=True, type=int, help="layer index to change the history metadata (where 0 is the base image)")
def change_metadata(dir: str, layer: int):
    image = OCIImageDir(dir)
    write_new_config_history(image, layer)


@cli.command()
@click.option("--dir", required=True, help="directory with the untar'd container image (from a docker save command)")
@click.option("--layer", required=True, type=int, help="layer index to read from (where 0 is the base image)")
@click.option("--path", required=True, help="the path within the layer to read the contents of")
def get_layer_path_read_contents(dir: str, layer: int, path: str):
    image = OCIImageDir(dir)

    digest = image.layer_blob_digest(layer)
    blob_path = image.blob_path(digest)
    new_layer_path = f"{dir}-verify-layer"

    extract_layer_tar(blob_path, new_layer_path)

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