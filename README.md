# Cloud Native Security North America 2021

- Official Schedule Posted: Wednesday, Aug 25
- Speaker Registration Deadline: Friday, September 3
- Pre-Recorded Video File Submission Deadline: Friday, Sept 10 by 11:59 PM PDT
- Slide Submission Deadline: Friday, October 1 by 11:59 PM PDT
- Event Date: October 12
## Submission
### Session Description
Building images can be surprisingly difficult, particularly if you need to use packages or applications that are not open and publically available. It's all too easy to end up with access tokens, credentials, or build artifacts left behind in non-obvious parts of an image. Once you have an image how certain are you that you've cleaned up properly and that it doesn't contain any secrets? Does it have any vulnerable software packages? Is your base image hiding information or unexpected content from you? This talk will show you common pitfalls that lead to information being hidden within an image (either wittingly or unwittingly) and how you can be sure there are no lurking surprises in your image before you publish it. I'll show how to automate these practices in a Tekton pipeline that both builds your image and acts as a quality gate for publication, because no-one wants to be the person with access keys sitting out in a registry.

### Benefits to the Ecosystem
Secrets or other sensitive material escaping into the wild inside of images is a real concern, and particularly relevant for folks building containers that do not include only open-source software. Image construction and storage is often not well understood by developers so even well-intentioned users can accidentally find themselves in trouble with information leakage inside of images. 

This talk will focus on the various circumstances that can lead to hidden information within images and further illustrate best practices to minimize these risks. Specifically by using SBOM tooling to make packaged software more transparent and auditable, secrets and vulnerability scanners to show specific risks in dependencies and other artifacts, and using Tekton to automate vetting built container images before publishing to a registry.

## Plan of action

- Image artifact quality gates:
    - secrets searching
    - inter-layer hidden files (e.g. development packages)
    - SBOM generation could not reach certain areas (permission denied or otherwise)
- SBOM generation + save as an artifact
- Scan SBOM with grype for vulnerability quality gate

## Projects
- Tekton
- Syft
- Grype

## Ideas

### Presentation Notes

Notes:
- -f should maybe show the report to stdout additionally?
- where do I stash the vulnerability report?

Hiding:
- secret in plan layer
- hidden layer has a secret
- vulnerability in a visible file

### Hiding things in images

- [ ] Extra unreferenced blob
- [ ] Content in whiteout files
    - [x] whiteout content via modification of existing whiteout
    - [x] whiteout content via addition of whiteout
    - [ ] whiteout content as symlink?
    - [ ] whiteout content as broken symlink?
    - [ ] whiteout content as hardlink?
    - [ ] opaque whiteout directory 
- [ ] Add files outside of the layer content areas
- [ ] Encode information into annotations
- [ ] Combining with non-distributable layers for just-in-time injection of material?
- [ ] Store payload content as extended attribute values across multiple files


The typical ways (not interested):
    - stegonography
    - encryption