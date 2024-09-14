const DB_NAME = 'doc-search-chanin';
const VERSION = 1;

class History {
  #id;
  #input;
  #result;

  constructor(row) {
    if (row !== undefined) this.setRow(row);
  }

  setRow(row) {
    this.#id = row.id;
    this.#input = row.input;
    this.#result = row.result;
  }

  setId(id) {
    this.#id = id;
  }
  setInput(input) {
    this.#input = input;
  }
  setResult(result) {
    this.#result = result;
  }

  getId() {
    return this.#id;
  }
  getInput() {
    return this.#input;
  }
  getResult() {
    return this.#result;
  }

  generateRow() {
    if (this.#id === undefined) {
      return {
        input: this.#input,
        result: this.#result,
      };
    }
    return {
      id: this.#id,
      input: this.#input,
      result: this.#result,
    };
  }
}

class IndexedDB {
  STORE_NAME;
  entity;

  conect() {
    return indexedDB.open(DB_NAME, VERSION);
  }

  async selectAll() {
    return new Promise((resolve, reject) => {
      const conect = this.conect();
      conect.onsuccess = (event) => {
        const db = event.target.result;
        const transaction = db.transaction([this.STORE_NAME], 'readonly');
        const objectStore = transaction.objectStore(this.STORE_NAME);
        const request = objectStore.getAll();

        request.onsuccess = (e) => {
          resolve({
            message: 'success',
            data: e.target.result.map((row) => {
              const entity = new this.entity(row);
              return entity;
            }),
          });
        };

        request.onerror = (e) => {
          reject({ message: e.target.error, data: undefined });
        };
      };
      conect.onerror = (event) => {
        reject({ message: event.target.error, data: undefined });
      };
    });
  }

  async innsert(row) {
    return new Promise((resolve, reject) => {
      const conect = this.conect();
      conect.onsuccess = (event) => {
        const db = event.target.result;
        const transaction = db.transaction([this.STORE_NAME], 'readwrite');
        const objectStore = transaction.objectStore(this.STORE_NAME);
        const request = objectStore.add(row);

        request.onsuccess = (event) => {
          const id = event.target.result;
          resolve({ message: 'success', id });
        };

        request.onerror = (e) => {
          reject({ message: e.target.error });
        };
      };
      conect.onerror = (event) => {
        reject({ message: event.target.error });
      };
    });
  }

  /**
   * @param {{init, db}[]} setUpDBList
   */
  initDB(setUpDBList) {
    this.conect().onupgradeneeded = (event) => {
      setUpDBList.forEach((v) => {
        console.log(v);
        v.init.call(v.db, event);
      });
    };
  }

  setUpDB() {
    return { init: this.initDB, db: this };
  }
}

class HistoryDB extends IndexedDB {
  STORE_NAME = 'history';
  entity = History;

  initDB(event) {
    const db = event.target.result;

    const objectStore = db.createObjectStore(this.STORE_NAME, {
      keyPath: 'id',
      autoIncrement: true,
    });
    objectStore.createIndex('input', 'input');
    objectStore.createIndex('result', 'result');
  }
}
