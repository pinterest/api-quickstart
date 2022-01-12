import readline from 'readline';
import { openSync, closeSync } from 'fs';

/**
 * Input is a container for a few user input functions that use readline.
 * It might be possible to use a higher-level package like prompt,
 * but readline works fine for the purposes of this demonstration code.
 */
export class Input {
  stdin_read() {
    this.stdin_data = new Promise(resolve => {
      process.stdin.setEncoding('utf8');
      let stdin_data = '';
      process.stdin.on('data', function(chunk) {
        stdin_data += chunk;
      });
      process.stdin.on('end', function() {
        resolve(stdin_data);
      });
    });
  }

  async stdin_line(str, resolve) {
    // Process piped input from stdin.
    process.stdout.write(str);
    if (!this.stdin_lines) {
      const stdin_data = await this.stdin_data;
      this.stdin_lines = stdin_data.split('\n');
    }
    const response = this.stdin_lines.shift();
    if (!response) {
      throw new Error('End of input');
    }
    process.stdout.write(response + '\n');
    resolve(response);
  }

  constructor() {
    if (process.stdin.isTTY) {
      // Interact with a human user.
      // Running readline.createInterface prevents the process from terminating
      // until rl.close is called.
      this.rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
        terminal: false // so that user input is not echoed
      });
    } else {
      // Running in test mode: retrieve all input from stdin.
      // Note: This mode is not tested by the unit tests because
      // it is primarily for use with integration tests.
      this.stdin_read();
    }
  }

  // This function converts readline.question to returning a Promise.
  async question(str) {
    if (process.stdin.isTTY) {
      // Request input from the user.
      return new Promise(resolve => this.rl.question(str, resolve));
    } else {
      // Get input from stdin.
      return new Promise(resolve => this.stdin_line(str, resolve));
    }
  }

  // Call this function to allow the process to exit. An alternative is to
  // call process.exit() explicitly when the process needs to terminate.
  close() {
    if (process.stdin.isTTY) {
      this.rl.close();
    }
  }

  // Simple pass-through interface for readline.
  async get(prompt) {
    return await this.question(prompt);
  }

  // Prompt for a numerical input between minimum and maximum.
  // If the default is not specified, the default is the minimum.
  async number(prompt, minimum, maximum, defaultValue) {
    if (!defaultValue) {
      defaultValue = minimum;
    }
    if (minimum === maximum) {
      return minimum;
    }
    if (minimum > maximum) {
      throw new Error(`minimum ${minimum} > maximum ${maximum}`);
    }

    // print optional prompt
    if (prompt) {
      console.log(prompt);
    }

    let strval, intval;
    while (true) {
      strval = await this.question(`[${defaultValue}] `);
      if (strval === '') {
        return defaultValue;
      }
      intval = parseInt(strval);

      if (minimum <= intval && intval <= maximum) { return intval; }

      console.log(
        `${strval} is not a number between ${minimum} and ${maximum}`
      );
    }
  }

  // Request the user to input one of a list of values. The input is
  // case-insensitive, but the return value is always a verbatim member
  // of the list.
  async one_of(prompt, one_of_list, defaultValue) {
    if (prompt) {
      console.log(prompt);
    }

    // keep a list of lowercase values for case insensitive lookup
    const one_of_list_lowercase = one_of_list.map(s => s.toLowerCase());

    while (true) {
      const raw = await this.question(`[${defaultValue}] `);
      const value = raw.toLowerCase(); // for case insensitive lookup
      if (value === '') {
        return defaultValue; // blank entry returns the default
      }
      const index = one_of_list_lowercase.indexOf(value);
      if (index >= 0) {
        return one_of_list[index];
      }
      console.log('input must be one of', one_of_list);
    }
  }

  // Input a pathname for a writable file.
  async path_for_write(prompt, defaultFile) {
    if (prompt) {
      console.log(prompt);
    }

    while (true) { // keep going until a valid path is found
      // get the path
      let path = await this.question(`[${defaultFile}] `);
      if (path === '') {
        path = defaultFile;
      }

      try { // exclusive write to see if the file exists
        const fd = openSync(path, 'wx');
        closeSync(fd); // path is writable, all is well
        return path;
      } catch (err) {
        if (err.code === 'EEXIST') { // file exists, prompt user
          if (await this.one_of(
            'Overwrite this file?', ['yes', 'no'], 'no') ===
              'no') {
            continue; // user requested not to overwrite
          } else {
            try { // verify that file is otherwise writable
              const fd = openSync(path, 'w');
              closeSync(fd); // path is writable, all is well
              return path;
            } catch {
              // some other kind of error: try again
            }
          }
        }
      }
      console.log('Error: can not write to this file.');
    }
  }
}
