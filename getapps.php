<?php
#$searchterm = $_POST['searchterm'];
$searchterm = $_GET["searchterm"];
$searchterm = escapeshellarg($searchterm);
system('python playTest.py ' . $searchterm);
?>
