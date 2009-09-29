<?php

include_once 'constants.php';
include_once LIB_PATH.'util.php';
include_once LIB_PATH.'ui.php';

$fb = get_fb();
$user = $fb->require_login();


echo render_header('New');

echo render_feedback_message($_REQUEST['result'], $_REQUEST['title']);


echo '<h2>我要吃</h2>';
echo '<fb:editor action="handlers/foodhandler.php">';
echo '<fb:editor-text label="名稱" name="title"/>';
echo '<fb:editor-textarea label="描述" name="description"/>';
echo '<fb:editor-buttonset>';
echo '<fb:editor-button value="新增" name="add"/>';
echo '<fb:editor-cancel href="newfood.php"/>';
echo '</fb:editor-buttonset>';
echo '</fb:editor>';


echo render_footer();
