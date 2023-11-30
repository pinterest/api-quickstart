<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Demonstration</title>
    <link rel="stylesheet" href="demo.css">
</head>
<body>
<div class="content_container">
<h1>Demonstration</h1>
<p>
This page demonstrates how to use the access token to call
Pinterest API endpoints.
</p>
<h2>User Account</h2>
<p>
Here is the user account information fetched from the API in JSON.
</p>
    <?php

     /**
      * This file demonstrates how to use the access token to call
      * Pinterest API endpoints.
      *
      * PHP version 8
      *
      * @category Quickstart
      * @package  Pinterest_API_Quickstart
      * @author   David Chaiken <chaiken@pinterest.com>
      * @license  Apache License Version 2.0, January 2004
      * @link     https://github.com/pinterest/api-quickstart
      */

    /**
     * Call the Pinterest API.
     *
     * @param string $url     The URL to call.
     * @param array  $headers The headers to send.
     *
     * @return array The result of the API call.
     */
    function Call_Pinterest_api($url, $headers)
    {
          $curl = curl_init();
        curl_setopt_array(
            $curl, array(
              CURLOPT_URL => $url,
              CURLOPT_RETURNTRANSFER => true,
              CURLOPT_ENCODING => "",
              CURLOPT_MAXREDIRS => 10,
              CURLOPT_TIMEOUT => 30,
              CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
              CURLOPT_HTTPHEADER => $headers
              )
        );
    
          $result_json = curl_exec($curl);
          $result = json_decode($result_json, true);
          curl_close($curl);
          return $result;
    }

    /* Typically, the access token would be stored in a database
     * indexed by the user's identifier. For this demo, we'll
     * just get it from the session.
     */
    session_start();
    $access_token = $_SESSION['access_token'];

    /* The access token is sent in the Authorization header. */
    $headers = array(
        "Authorization:" . 'Bearer ' . $access_token
    );

    /* https://developers.pinterest.com/docs/api/v5/#tag/user_account */
    $url = "https://api.pinterest.com/v5/user_account";
    $result = Call_Pinterest_api($url, $headers);

    /* format JSON for display */
    $result_pp
        = json_encode($result, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
    ?>
    <p>
    <?php echo $result_pp ?>
    </p>
    <p>
    Here are some of the fields from the user account information extracted
    with PHP.
    </p>
    <p>
    <img width="150" src="<?php echo $result['profile_image'] ?>">
    <br/>
    <b>Username:</b> <?php echo $result['username'] ?>
    <br/>
    <b>Identifier:</b> <?php echo $result['id'] ?>
    </p>
<h2>Pin</h2>
<p>
Here is the first regular (static image) Pin in the user's account in JSON.
</p>
    <?php
    /* https://developers.pinterest.com/docs/api/v5/#tag/pins */
    $url = "https://api.pinterest.com/v5/pins"
         . "?page_size=1&creative_types=REGULAR";
    $result = Call_Pinterest_api($url, $headers);

    /* format JSON for display */
    $result_pp
        = json_encode($result, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
    $image = $result['items'][0]['media']['images']['150x150']['url']
    ?>
    <p>
    <?php echo $result_pp ?>
    </p>
    <p>
    Here are some of the fields from the Pin information extracted with PHP.
    </p>
    <p>
    <img src="<?php echo $image ?>">
    <br/>
    <b>Identifier:</b> <?php echo $result['items'][0]['id'] ?>
    <br/>
    <b>Link:</b> <?php echo $result['items'][0]['link'] ?>
    </p>
    <h2>The End</h2>
    <p>
    That's it for the demo. If you want to see it again, click this button:
    </p>
    <p>
    <a href="/">
    <input class="button" type="Submit" value="Start Over">
    </a>
    </p>
</div>
</body>
</html>
