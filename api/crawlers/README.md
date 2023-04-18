<h1>Google shared spreadsheet Crawlers</h1>

<h2>Usage</h2>
<ul>
<li>You have export docs ids to your environment variables, for example your docs links are (UPD links are broken now :) )
 <ol>
    <li>Reviews: <a href="https://docs.google.com/spreadsheets/d/1iSR0bR0TO5C3CfNv-k1bxrKLD5SuYt_2HXhI2yq15Kg/edit#gid=0">https://docs.google.com/spreadsheets/d/1iSR0bR0TO5C3CfNv-k1bxrKLD5SuYt_2HXhI2yq15Kg/edit#gid=0</a></li>
    <li>Products: <a href="https://docs.google.com/spreadsheets/d/1roypo_8amDEIYc-RFCQrb3WyubMErd3bxNCJroX-HVE/edit#gid=0">https://docs.google.com/spreadsheets/d/1roypo_8amDEIYc-RFCQrb3WyubMErd3bxNCJroX-HVE/edit#gid=0</a></li>
 </ol>
your env vars should be: 
<pre><code>REVIEW_DOC_ID=1iSR0bR0TO5C3CfNv-k1bxrKLD5SuYt_2HXhI2yq15Kg
PRODUCT_DOC_ID=1roypo_8amDEIYc-RFCQrb3WyubMErd3bxNCJroX-HVE
... other postgres and flask envs ...</code></pre></li>
<li><pre><code>cd api && export $(cat ../.env | xargs)
flask parse</code></pre></li></ul>
