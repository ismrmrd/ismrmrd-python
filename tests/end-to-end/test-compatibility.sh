#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(dirname "${BASH_SOURCE[0]}")
PROJECT_DIR=$(realpath "${SCRIPT_DIR}/../..")

if [ -n "${HOST_WORKSPACE_DIR:-}" ]; then
    WORKDIR="${HOST_WORKSPACE_DIR:-}"
else
    WORKDIR="$(pwd)"
fi

rm -rf testdata.h5
rm -rf *.ismrmrd

# Generate phantom dataset using published C++ tools
docker run --rm -v "${WORKDIR}":/tmp ghcr.io/ismrmrd/ismrmrd ismrmrd_generate_cartesian_shepp_logan -o /tmp/testdata.h5 -n 0.0

# Generate reference reconstructed image(s)
docker run -i --rm -v "${WORKDIR}":/tmp ghcr.io/ismrmrd/ismrmrd ismrmrd_hdf5_to_stream -i /tmp/testdata.h5 --use-stdout \
    | docker run -i --rm ghcr.io/ismrmrd/ismrmrd ismrmrd_stream_recon_cartesian_2d --use-stdin --use-stdout \
    > reference.ismrmrd


# Pipe it through the Python ProtocolSerializer to test compatibility
docker run --rm -i -v "${WORKDIR}":/tmp ghcr.io/ismrmrd/ismrmrd \
    /bin/bash -c "ismrmrd_hdf5_to_stream -i /tmp/testdata.h5 --use-stdout" \
    | python "${PROJECT_DIR}"/utilities/ismrmrd_copy_stream.py > phantom.ismrmrd

# Reconstruct the image using the Python-generated protocol stream
# Pipe the result through the Python ProtocolSerializer again to test compatibility
docker run --rm -i -v "${WORKDIR}":/tmp ghcr.io/ismrmrd/ismrmrd \
    /bin/bash -c "ismrmrd_stream_recon_cartesian_2d --use-stdin --use-stdout" \
    < phantom.ismrmrd \
    | python "${PROJECT_DIR}"/utilities/ismrmrd_copy_stream.py > reconstructed.ismrmrd

# Compare the images
python "${SCRIPT_DIR}"/validate_results.py --reference reference.ismrmrd --testdata reconstructed.ismrmrd