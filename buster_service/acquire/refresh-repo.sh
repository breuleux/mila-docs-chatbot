#!/bin/bash

set -e

TAG=last-generated

mkdir -p $BASE
cd $BASE

if [ ! -d $REPO ]; then
    echo "Cloning the repo..."
    git clone "https://github.com/$REPO" $REPO
    echo "Creating a virtual environment..."
    python3 -m venv $REPO/.venv
fi

cd $REPO
git checkout $BRANCH
git pull

PREVIOUS=$(git rev-parse --verify $TAG 2>/dev/null || echo "n/a")
LATEST=$(git rev-parse --verify $BRANCH 2>/dev/null)

if [ "$PREVIOUS" = "$LATEST" ]; then
    echo "No changes since the last generation"
    exit 1
fi
echo "Commit at $BRANCH is new, re-generating"

source .venv/bin/activate
pip install -U pip
pip install -r $REQFILE
sphinx-build -b html docs/ docs/_build/
git tag -f $TAG

exit 0
