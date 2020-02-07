<html>
    <head>
        <title>Tunes2u</title>
        <style>
        html { 
          background: url(1.png) no-repeat center center fixed; 
          -webkit-background-size: cover;
          -moz-background-size: cover;
          -o-background-size: cover;
          background-size: cover;
        }
        </style>
    </head>
    <body>
        <script>
            window.location.href = 'getfile.php?file=<?php echo $_GET['file'];?>';
        </script>
    </body>
</html>
