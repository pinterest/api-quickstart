<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Pinterest API Example in PHP</title>
    <link rel="stylesheet" href="demo.css">
</head>
<body>
<div class="content_container">
<h1>Pinterest API Example in PHP</h1>
<p>
This sample application demonstrates how to use the Pinterest API in PHP.
It first uses OAuth 2.0 to get an access token, and then uses the access token
to get user and Pin information from the API.
</p>
<?php
/**
 * This file demonstrates how to use OAuth 2.0 to get an access token.
 * It handles both the start of the flow (Initial Page) and the OAuth
 * callback. It would be a bit cleaner to split these two functions into
 * different paths, but the two are combined here for compatibility with
 * the other language examples in this repository.
 *
 * PHP version 8
 *
 * @category Quickstart
 * @package  Pinterest_API_Quickstart
 * @author   David Chaiken <chaiken@pinterest.com>
 * @license  Apache License Version 2.0, January 2004
 * @link     https://github.com/pinterest/api-quickstart
 */

/* This code is common to both the initial page and the callback page. */
session_start(); /* Reminder: this code requires PHP version 8. */
$client_id = getenv('PINTEREST_APP_ID');
$redirect_uri = 'http://localhost:8085/';

if (!$client_id) {
    ?>
    <p>
    <b>
    You must run ". ../common/scripts/api_env" before starting the
    PHP server to run this demo.
    </b>
    </p>
    <?php
    exit;
}

/* If the GET request for this page has a code parameter, then this is the
 * callback from the OAuth 2.0 authorization page. The following code processes
 * the callback.
 */
if (array_key_exists('code', $_GET)) {
    ?>
    <h2>Callback</h2>
    <p>
    This page is the callback from the OAuth 2.0 authorization page.
    It should be displayed when following the demo without automatic
    redirect or if there is some sort of error.
    </p>
    <p>
    The way that this page knows that this is the callback is because
    the GET request for this page has a code parameter.
    You can see this code in the address bar of the browser.
    </p>
    <p>
    The code (which should normally be kept secret) is:
        <?php echo $_GET['code'] ?>
    </p>
    <?php
    /* Check to see if the state parameter has the auto direct prefix. */
    if (str_starts_with($_GET['state'], 'auto_redirect_')) {
        /* Automatic redirect requested. This is the normal application flow. */
        $auto_redirect = true;
        $expected_state = 'auto_redirect_' . $_SESSION['oauth_state'];
    } else {
        /* No automatic redirect requested. This is for demonstration purposes. */
        $auto_redirect = false;
        $expected_state = $_SESSION['oauth_state'];
    }
    ?>
    <p>
    The state parameter is a random string that is generated by the application
    on the initial page. It is used to prevent cross-site request forgery attacks.
    If you look at the request in the address bar of the browser, you'll see the
    state parameter in the URL that was generated by the Pinterest OAuth server.
    </p>
    <?php
    if ($_GET['state'] == $expected_state) {
        ?>
       <p>
        The state parameter in the request matches the state in the session, so the
        request is valid. This state is currently: <?php echo $expected_state ?>
        </p>
        <?php
    } else {
        ?>
       <p>
        <b>
        Security Issue: The state in the request does not match the state
        in the session.
        </b><br/>
        Expected: <?php echo $expected_state ?><br/>
        Actual: <?php echo $_GET['state'] ?><br/>
        </p>
        <p>
        To recover from this problem, you can click this button to start over:
        </p>
        <p>
        <a href="/"><input class="button" type="Submit" value="Start Over"></a>
        </p>
        <?php
        exit;
    }
    ?>
    <h2>Access Token</h2>
    <p>
    The next step is to use the code returned by the Pinterest API
    to get an access token.
    </p>
    <?php
    /* https://developers.pinterest.com/docs/api/v5/#tag/oauth */
    $auth_url = "https://api.pinterest.com/v5/oauth/token";

    /* The client ID and client secret are used to create a
     * Basic authorization header, which is required to get an access token.
     */
    $client_secret = getenv('PINTEREST_APP_SECRET');
    $authorization = base64_encode($client_id . ':' . $client_secret);
    $headers = array(
            "Authorization:" . 'Basic ' . $authorization
    );

    /* These parameters are required to get an access token. */
    $params = array(
        "grant_type" => "authorization_code",
        "code"        => $_GET['code'],
        "redirect_uri" => $redirect_uri,
    );

    $data = http_build_query($params); /* encode URL parameters */
    $curl = curl_init();
    curl_setopt_array(
        $curl, array(
        CURLOPT_URL => $auth_url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_ENCODING => "",
        CURLOPT_MAXREDIRS => 10,
        CURLOPT_TIMEOUT => 30,
        CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
        CURLOPT_CUSTOMREQUEST => "POST",
        CURLOPT_POSTFIELDS => $data,
        CURLOPT_HTTPHEADER => $headers
        )
    );

    $result_json = curl_exec($curl); /* call the Pinterest API */
    /* extract JSON into structure */
    $result = json_decode($result_json, true);
    curl_close($curl);

    if (array_key_exists('access_token', $result)) {
        $_SESSION['access_token'] = $result['access_token'];
        ?>
        <p>
        Here is the access token returned by the API:<br/>
        <?php echo $_SESSION['access_token'] ?>
        </p>
        <p>
        Ordinarily, this access token would be saved in a database or other
        persistent storage. For this demo, it is saved in the session. It also
        shouldn't be printed out in cleartext, but it's printed here for
        demonstration purposes.
        </p>
        <?php
        if ($auto_redirect) {
            /* Redirect the browser to the demo. This is a typical
             * application flow.
             */
            header('Location: /demo.php');
            exit;
        }
        ?>
        <h2>Next Step</h2>
        <p>
        Since this instance of the demo does not automatically redirect,
        the next step is to click this button to continue to the demo page:
        </p>
        <p>
        <a href="/demo.php"><input class="button" type="Submit" value="Continue"></a>
        </p>
        <p>
        Or you can click this button to start over:
        </p>
        <p>
        <a href="/"><input class="button" type="Submit" value="Start Over"></a>
        </p>
        <?php
    } else { /* The API did not return an access token. */
        ?>
        <p>
        There was an error getting the access token.
        </p>
        <p>
        Here is the JSON returned by the API that should provide
        insight into the error:<br/>
        <?php echo $result_json ?>
        </p>
        <p>
        To recover from this problem, you can click this button to start over:
        </p>
        <p>
        <a href="/"><input class="button" type="Submit" value="Start Over"></a>
        </p>
        <?php
    }
} else {
    /* If the GET request for this page does not have a code parameter, then this
     * is the initial page. The following code generates the authorization URL
     * and provides instructions to the developer on next steps.
     */
    $_SESSION['oauth_state'] = bin2hex(random_bytes(16));
    $url_prefix = "https://www.pinterest.com/oauth/?"
                . "consumer_id=" . $client_id
                . "&redirect_uri=" . $redirect_uri
                . "&response_type=code"
                . "&refreshable=true"
                . "&scope=user_accounts:read,pins:read,boards:read"
                . "&state=";
    $url_no_redirect = $url_prefix . $_SESSION['oauth_state'];
    /* The auto_redirect_ prefix signals the callback page to redirect
     * automatically to the demo page.
     */
    $url_with_redirect
        = $url_prefix . "auto_redirect_" . $_SESSION['oauth_state'];
    ?>
    <h2>Initial Page</h2>
    <p>
    Click this button to see each step in the OAuth process:
    </p>
    <p>
    <a href="<?php echo $url_no_redirect ?>">
    <input class="button" type="Submit" value="No Redirect">
    </a> 
    </p>
    <p>
    For real applications, the callback page should not be shown to the user.<br/>
    Click this button to see this normal flow where the callback page is skipped.
    </p>
    <p>
    <a href="<?php echo $url_with_redirect ?>">
    <input class="button" type="Submit" value="Redirect">
    </a>
    </p>
    <?php
}
?>
</div>
</body>
</html>