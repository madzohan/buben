# API reference draft
###List Product Reviews
<ul>
    <li>Returns Product identified by id and its Reviews, maximum of 5 records per page (сursor pagination)
    <p>>ToDo: implement cache based on this answer https://stackoverflow.com/a/42426019/3033586</p>
    <pre><code>GET /api/v1/products/{product_id}</code></pre>
    </li>
    <li>Example requests and responses
    <ul>
        <li>using <b>curl</b>
            <pre><code>curl http://{domain}/api/v1/products/{product_id} -v</code></pre>
        </li>
        <li>response

<pre>Status: 200
Location: /api/v1/products/{{product_id}}


{
  "products": [
      {
        "id":   {{product_id}},
        "asin": "B06X12Z3IU",
        "title": "UFO",
        "reviews": [
            {
              "id":   1,
              "title": "One Star",
              "body": "sound quality POOR"
            }
        ]
      }
   ]
}</pre>
</li></ul></li></ul>
<hr />

###Create Product Reviews
<ul>
    <li>Creates a review for product identified by id
    <pre><code>PUT /api/v1/products/{product_id}/reviews/create.json</code></pre></li>
    <li>Example requests and responses
            <ul>
                <li>using <b>curl</b>
                    <pre><code>curl http://{domain}/api/v1/products/{product_id}/reviews/create.json \
                      -d '{"title": "Nice!", "body": "Please return my money back!"}' \
                      -H "Content-Type: application/json" -X PUT -v</code></pre>
                </li>
                <li>response

<pre>Status: 201 Created
Location: /api/v1/products/{{product_id}}/reviews/{{new-review-id}}.json


{
  "products": {
    "id":   {{product_id}},
    "asin": "B06X12Z3IU",
    "title": "UFO",
    "reviews": [
        {
            "id": {{new-review-id}},
            "title": "Nice!",
            "body": "Please return my money back!"
        }
    ]
  }
}</pre>
</li></ul></li></ul>
<hr />

### dev notes
<ul><li>working with migrations<pre><code>export $(cat ../.env | xargs) && flask db migrate -m "Initial: product, review"
flask db upgrade</code></pre></li>
<li>local Pipenv for generating Pipfile.lock
<pre><code>export PIPENV_PIPFILE=/abs_path_to/Pipfile
pipenv --venv
pipenv update</code></pre></li>
</ul>