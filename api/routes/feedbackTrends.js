var express = require('express');
var router = express.Router();
var { spawn } = require('child_process');

// En Çok Artış Gösteren İlk 5 Geri Bildirim Kategorisini Getir
router.get('/topIncreasingCategories', async (req, res) => {
    try {
        const pythonProcess = spawn('python', ['python_scripts/feedback_arima.py']);
        let dataBuffer = '';

        pythonProcess.stdout.on('data', (data) => {
            dataBuffer += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
            console.error(`Python Hatası: ${data}`);
        });

        pythonProcess.on('close', (code) => {
            if (code === 0) {
                try {
                    const result = JSON.parse(dataBuffer);
                    res.json(result);
                } catch (error) {
                    res.status(500).json({ error: 'JSON Parse Hatası', details: error.message });
                }
            } 
            else{
                console.error("Python Script Hatası:", err.stack);
                res.status(500).json({ error: "Python Script Hatası", details: error.message });

            }
        });
    } 
    catch (error) {
        console.error('API Hatası:', error);
        res.status(500).json({ error: 'Sunucu Hatası' });
    }
});

module.exports = router;