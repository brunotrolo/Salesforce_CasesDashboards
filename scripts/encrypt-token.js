#!/usr/bin/env node
/* Gera docs/data/token.enc.json com o token cifrado (AES-256-GCM + PBKDF2-SHA256).
   O arquivo pode ser commitado com segurança: sem a passphrase é ilegível.
   Uso: node scripts/encrypt-token.js [--token ghp_xxx]
   A passphrase é digitada sem eco (não fica no histórico do terminal). */

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const tokenArg = args.indexOf('--token') !== -1 ? args[args.indexOf('--token') + 1] : null;

function promptHidden(query) {
    return new Promise((resolve) => {
        process.stdout.write(query);
        process.stdin.setRawMode(true);
        process.stdin.resume();
        let buf = '';
        process.stdin.on('data', (chunk) => {
            const s = chunk.toString();
            for (const c of s) {
                if (c === '\r' || c === '\n') {
                    process.stdout.write('\n');
                    process.stdin.setRawMode(false);
                    process.stdin.pause();
                    resolve(buf);
                } else if (c === '\u0003') {
                    process.exit(130);
                } else if (c === '\u007f') {
                    buf = buf.slice(0, -1);
                    process.stdout.write('\b \b');
                } else {
                    buf += c;
                    process.stdout.write('*');
                }
            }
        });
    });
}

(async () => {
    const token = tokenArg || (await promptHidden('Token GitHub: '));
    if (!token) {
        console.error('Token vazio.');
        process.exit(1);
    }
    const pass1 = await promptHidden('Passphrase para cifrar o token: ');
    const pass2 = await promptHidden('Repita a passphrase: ');
    if (!pass1 || pass1 !== pass2) {
        console.error('Passphrases não conferem.');
        process.exit(1);
    }

    const iterations = 250000;
    const salt = crypto.randomBytes(16);
    const iv = crypto.randomBytes(12);
    const key = crypto.pbkdf2Sync(pass1, salt, iterations, 32, 'sha256');
    const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
    const enc = Buffer.concat([cipher.update(token, 'utf8'), cipher.final()]);
    const tag = cipher.getAuthTag();

    const blob = {
        kdf: 'PBKDF2-SHA256',
        iterations,
        salt: salt.toString('base64'),
        iv: iv.toString('base64'),
        data: Buffer.concat([enc, tag]).toString('base64')
    };

    const out = path.join(__dirname, '..', 'docs', 'data', 'token.enc.json');
    fs.writeFileSync(out, JSON.stringify(blob, null, 2) + '\n');
    console.log(`Token cifrado salvo em ${out}`);
    console.log('Commit o arquivo e, em cada PC novo, o site pedirá apenas a passphrase.');
})();