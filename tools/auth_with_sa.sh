#!/bin/bash
# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/bin/bash

set -f

# Hardcoded the project ID for all local development.
declare -a EnvVars=(
  "SA_EMAIL"
)
for variable in "${EnvVars[@]}"; do
  if [[ -z "${!variable}" ]]; then
    printf "$variable is not set.\n"
    exit 1
  fi
done

mkdir -p .tmp
gcloud iam service-accounts keys create .tmp/sa-key.json --iam-account=$SA_EMAIL

gcloud auth activate-service-account --key-file=.tmp/sa-key.json
