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

        session_start();
        $access_token = $_SESSION['access_token'];

        $headers = array(
            // "Content-Type: application/x-www-form-urlencoded",
                "Authorization:" . 'Bearer ' . $access_token
        );

        // https://developers.pinterest.com/docs/api/v5/#tag/user_account
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
        <?php
        echo '<img width="150" src="' . $result['profile_image'] . '">' . "\n";
        echo '<br/><b>Username:</b> ' . $result['username'] . "\n";
        echo '<br/><b>Identifier:</b> ' . $result['id'] . "\n";
        ?>
        </p>
<h2>Pin</h2>
<p>
Here is the first regular (static image) Pin in the user's account in JSON.
</p>
        <?php
        // https://developers.pinterest.com/docs/api/v5/#tag/pins
        $url = "https://api.pinterest.com/v5/pins"
             . "?page_size=1&creative_types=REGULAR";
        $result = Call_Pinterest_api($url, $headers);

        /* format JSON for display */
        $result_pp
            = json_encode($result, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
        ?>
        <p>
        <?php echo $result_pp ?>
        </p>
        <p>
        Here are some of the fields from the Pin information extracted with PHP.
        </p>
        <p>
        <?php
        echo '<img src="'
             . $result['items'][0]['media']['images']['150x150']['url']
             . '">' . "\n";
        echo '<br/><b>Identifier:</b> ' . $result['items'][0]['id'] . "\n";
        echo '<br/><b>Link:</b> ' . $result['items'][0]['link'] . "\n";
        ?>
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
