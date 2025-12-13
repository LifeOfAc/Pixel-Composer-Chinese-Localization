const fs = require('fs');
const zlib = require('zlib');
const path = require('path');

async function extractJsonFromPxc(inputFile) {
    try {
        const buffer = fs.readFileSync(inputFile);
        const zlibStart = buffer.indexOf(Buffer.from('789C', 'hex'));
        let zlibEnd = buffer.length;
        for (let i = buffer.length - 1; i > zlibStart; i--) {
            if (buffer[i] !== 0x00) {
                zlibEnd = i + 1;
                break;
            }
        }
        const compressedData = buffer.slice(zlibStart, zlibEnd);
        const decompressed = await new Promise((resolve, reject) => {
            zlib.inflate(compressedData, (err, result) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(result);
                }
            });
        });
        const cleanData = decompressed.toString('utf8').replace(/\0+$/g, '');
        const jsonData = JSON.parse(cleanData);

        const parsedPath = path.parse(inputFile);
        const outputFile = path.join(parsedPath.dir, parsedPath.name + '.json');

        const formattedJson = JSON.stringify(jsonData, null, 2);
        fs.writeFileSync(outputFile, formattedJson);
        console.log(`JSON已保存到: ${outputFile}`);

    } catch (error) {
        console.error('处理失败:', error.message);
    }
}

//示例
extractJsonFromPxc('./黑色.pxc');