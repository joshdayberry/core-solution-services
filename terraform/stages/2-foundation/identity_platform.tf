/**
 * Copyright 2023 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

resource "google_identity_platform_project_default_config" "default" {
  depends_on   = [module.project_services]
  sign_in {
    email {
      enabled           = true
      password_required = false
    }
  }
}

resource "google_apikeys_key" "idp_api_key" {
  depends_on   = [module.project_services]
  name         = "idp-api-key"
  display_name = "API Key for Identity Platform"

  restrictions {
    api_targets {
      service = "identitytoolkit.googleapis.com"
    }
  }
}
