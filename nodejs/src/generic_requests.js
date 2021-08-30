import stream from 'stream';
import { promisify } from 'util';
import fs from 'fs';
import got from 'got';

const pipeline = promisify(stream.pipeline);

// Use streaming HTTP request to download a file. See:
//  https://www.npmjs.com/package/got#streams
export async function download_file(url, path) {
  await pipeline(got.stream(url), fs.createWriteStream(path));
}
