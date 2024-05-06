const express = require('express');
const multer = require('multer')
const path = require('path')
const { exec } = require('child_process');


//Setting the path of the uploaded files and renaming it appropriately
const storage = multer.diskStorage({
    destination:function(req,file,cb){
        cb(null,'./uploads');
    },
    filename:function(req,file,cb){
        cb(null,file.originalname);
    }
});

const upload = multer({storage})
const app = express();
app.set('view engine','ejs');
app.use(express.static(path.join(__dirname,'images'))) //Setting the static file path

const port = process.env.port || 3000;

//Uploading CSV
app.post('/upload',upload.single('file'),(req, res) => {
    if (!req.file) {
        return res.status(400).send('No file uploaded.');
    }
    const { filename } = req.file;
    const pythonScript = `python anomaly_detection.py uploads/${filename}`;

    //Running the python Script
    exec(pythonScript, (error, stdout, stderr) => {
        if (error) {
          console.error(`Error executing Python script: ${error}`);
          res.status(500).send('An error occurred');
          return;
        }
        const output = JSON.parse(stdout);
        // console.log(output);
        res.render('results', { output });
      });

});
app.get('/',(req,res)=>{
    const data = {};
    res.render('index');
});

app.listen(port,()=>{
    console.log(`Listening on port ${port}`)
});