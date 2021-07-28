import readline from 'readline';

/**
 * Input is a container for a few user input functions that use readline.
 * It might be possible to use a higher-level package like prompt,
 * but readline works fine for the purposes of this demonstration code.
 */
export class Input {
  constructor() {
    // Running readline.createInterface prevents the process from terminating
    // until rl.close is called.
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      terminal: false // so that user input is not echoed
    });
  }

  // This function converts readline.question to returning a Promise.
  async question(str) {
    return new Promise(resolve => this.rl.question(str, resolve));
  }

  // Call this function to allow the process to exit. An alternative is to
  // call process.exit() explicitly when the process needs to terminate.
  close() {
    this.rl.close();
  }

  // Simple pass-through interface for readline.
  async get(prompt) {
    return await this.question(prompt);
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
      for (let idx = 0; idx < one_of_list.length; ++idx) {
        if (value === one_of_list_lowercase[idx]) {
          return one_of_list[idx];
        }
      }
      console.log('input must be one of', one_of_list);
    }
  }
}
