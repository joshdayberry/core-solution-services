# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -e

declare -a EnvVars=(
  "SKAFFOLD_NAMESPACE"
  "PROJECT_ID"
  "GSA_NAME"
  "KSA_NAME"
)

for variable in "${EnvVars[@]}"; do
  if [[ -z "${!variable}" ]]; then
    printf "$variable is not set.\n"
    exit 1
  fi
done

echo
echo "SKAFFOLD_NAMESPACE=${SKAFFOLD_NAMESPACE}"
echo "PROJECT_ID=${PROJECT_ID}"
echo "GSA_NAME=${PROJECT_ID}"
echo "KSA_NAME=${PROJECT_ID}"
echo

declare EXISTING_KSA=$(kubectl get sa -n ${SKAFFOLD_NAMESPACE} | egrep -i "^${KSA_NAME} ")
printf "\nCreating kubernetes service account on the cluster ...\n"
if [[ "$EXISTING_KSA" = "" ]]; then
  kubectl create serviceaccount -n ${SKAFFOLD_NAMESPACE} ${KSA_NAME}
fi

printf "\nAdding Service Account IAM policy ...\n"
gcloud iam service-accounts add-iam-policy-binding \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:${PROJECT_ID}.svc.id.goog[${SKAFFOLD_NAMESPACE}/${KSA_NAME}]" \
  ${GSA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com

printf "\nConnecting ksa with Service Account ...\n"
kubectl annotate serviceaccount \
  --overwrite \
  --SKAFFOLD_NAMESPACE ${SKAFFOLD_NAMESPACE} \
  ${KSA_NAME} \
  iam.gke.io/gcp-service-account=${GSA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
