## Approach

With a removal dockerfile line (`RUN rm <file>`) modify the existing whiteout file to have a payload. 
This involves recreating the layer tar + surrounding metadata.

## Results

- Crafting and importing was successful, using the image works and the file is still hidden

- The image cannot be extracted from the docker daemon:
    ```bash
    $ skopeo copy --override-os linux --insecure-policy docker-daemon:localhost/whiteout-content:modified docker-archive:/tmp/place.tar

    FATA[0000] Error initializing source docker-daemon:localhost/whiteout-content:modified: Error loading image from docker engine: Error response from daemon: open /var/lib/docker/overlay2/61a73ba2ecf835ed47e6481eada5b0f64f0dc00a0beb8fcda5a8c9ef8c0b4a29/merged/somewhere/.wh.nothing.txt: no such file or directory
    ```

- The image cannot be distributed:
    ```
    $docker push anchore/test_images:alex-cloud-native-conf-2021-whiteout-content

    The push refers to repository [docker.io/anchore/test_images]
    732e76c7cfa2: Pushing  6.144kB
    4f1e92ce95d8: Pushed
    910fa59606b7: Pushed
    0fd05bf2930d: Mounted from library/busybox
    open /var/lib/docker/overlay2/61a73ba2ecf835ed47e6481eada5b0f64f0dc00a0beb8fcda5a8c9ef8c0b4a29/merged/somewhere/.wh.nothing.txt: no such file or directory
    ```

## Conclusion

Possible but not useful