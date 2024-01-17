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

"""
  Delete dummy firestore collections created earlier
"""
import firebase_admin
from firebase_admin import firestore

app = firebase_admin.initialize_app()
db = firestore.client()

db.collection("batch_jobs").document("batch_jobs_dummy").delete()
db.collection("user_chats").document("user_chats_dummy").delete()
db.collection("user_queries").document("user_queries_dummy").delete()
db.collection("query_documents").document("query_documents_dummy").delete()
