document.addEventListener('DOMContentLoaded', () => {
  
  bsCustomFileInput.init();
  
  const modal = new bootstrap.Modal(document.querySelector('#modal'));

  const allFileCheckboxElem = document.querySelector('#all-file-checkbox');
  if (allFileCheckboxElem) {
    allFileCheckboxElem.addEventListener('change', (event) => {
      const { checked } = event.target;
      document.querySelectorAll('.file-checkbox').forEach(e => e.checked = checked);
    });
  }

  document.querySelector('#load-document-btn').addEventListener('click', async () => {
    showModal(generateLoadingElem());
    try {
      const response = await fetch('/loadDocument', {
        method: 'POST'
      });
      const text = await response.text();
      if (!response.ok) {
        throw new Error(text);
      }
      updateModalBody(generateMessageElem(text));
    } catch (error) {
      console.error('Error:', error);
      updateModalBody(generateMessageElem(error, true));
    }
  });

  document.querySelector('#search-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const { value } = document.querySelector('#search-input');

    if (!value) return;
    hideMessage();
    try {
      const response = await fetch('/searchForm', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ input: value })
      });      
      if (!response.ok) {
        throw new Error(await response.text());
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      while (true) {
        const { done, value } = await reader.read();        
        if (done) {
          parseMarkdownToHtml();
          break;
        };
        showResponse(decoder.decode(value));
      }
    } catch (error) {
      console.error(error);
      showError(error);
    }
  });

  document.querySelector('#search-input').addEventListener('input', (e) => {
    const height =  Math.min(e.target.scrollHeight, 300);
    e.target.style.height = height + 'px';
  });

  const showError = (message) => {
    const responseErrorMessageElem = document.querySelector('#response-error-message');
    responseErrorMessageElem.innerText = message;
    responseErrorMessageElem.parentElement.classList.remove('d-none');
  }

  const showResponse = (message) => {
    const responseElem = document.querySelector('#response');
    responseElem.innerHTML += message;
    responseElem.classList.remove('d-none');
  }

  const parseMarkdownToHtml = () => {
    const responseElem = document.querySelector('#response');
    responseElem.innerHTML = marked.parse(responseElem.innerHTML);
    hljs.highlightAll();
  }

  const hideMessage = () => {
    const responseErrorMessageElem = document.querySelector('#response-error-message');
    responseErrorMessageElem.innerText = '';
    responseErrorMessageElem.parentElement.classList.add('d-none');
    const responseElem = document.querySelector('#response');
    responseElem.innerHTML = '';
    responseElem.classList.add('d-none');
  }

  const showModal = (elem) => {
    updateModalBody(elem);
    modal.show();
  }

  const updateModalBody = (elem) => {
    const modalBodyElem = document.querySelector('#modal-body');
    modalBodyElem.innerHTML = '';
    modalBodyElem.appendChild(elem);
  }
});

const generateLoadingElem = () => {
  const elem = document.createElement('div');
  elem.classList.add('d-flex', 'align-items-center', 'justify-content-center', 'p-5');
  elem.innerHTML = `<span class='fs-3'>Documents Loading</span>
    <div class='spinner-grow spinner-grow-sm ms-2' role='status'>
      <span class='visually-hidden'>Loading...</span>
    </div>
    <div class='spinner-grow spinner-grow-sm ms-2' role='status'>
      <span class='visually-hidden'>Loading...</span>
    </div>
    <div class='spinner-grow spinner-grow-sm ms-2' role='status'>
      <span class='visually-hidden'>Loading...</span>
    </div>`;
  return elem;
}
const generateMessageElem = (text, isError=false) => {
  const elem = document.createElement('div');
  elem.classList.add('d-flex', 'align-items-center', 'justify-content-center', 'p-5');
  elem.innerHTML = `<span class='fs-3 ${isError ? 'text-danger' : 'text-success'}'>${text}</span>`;
  return elem;
}
