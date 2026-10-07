const cameraButton = document.querySelector('#cameraButton');
const uploadButton = document.querySelector('#uploadButton');
const cameraInput = document.querySelector('#cameraInput');
const fileInput = document.querySelector('#fileInput');
const dropZone = document.querySelector('#dropZone');
const uploadOptions = document.querySelector('#uploadOptions');
const previewArea = document.querySelector('#previewArea');
const previewImage = document.querySelector('#previewImage');
const fileName = document.querySelector('#fileName');
const fileMeta = document.querySelector('#fileMeta');
const classifyButton = document.querySelector('#classifyButton');
const chooseAgainButton = document.querySelector('#chooseAgainButton');
const loadingState = document.querySelector('#loadingState');
const resultCard = document.querySelector('#resultCard');
const errorMessage = document.querySelector('#errorMessage');
const resetButton = document.querySelector('#resetButton');
const stepNumber = document.querySelector('#stepNumber');

let selectedFile = null;
let previewUrl = null;

const setStep = (step) => {
  stepNumber.textContent = String(step).padStart(2, '0');
};

const showError = (message) => {
  errorMessage.textContent = message;
  errorMessage.hidden = false;
};

const clearError = () => {
  errorMessage.textContent = '';
  errorMessage.hidden = true;
};

const formatBytes = (bytes) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

const resetView = () => {
  selectedFile = null;
  if (previewUrl) URL.revokeObjectURL(previewUrl);
  previewUrl = null;
  previewImage.src = '';
  uploadOptions.hidden = false;
  dropZone.hidden = false;
  previewArea.hidden = true;
  loadingState.hidden = true;
  resultCard.hidden = true;
  document.querySelector('#fallbackNote').hidden = true;
  clearError();
  setStep(1);
};

const handleFile = (file) => {
  clearError();
  if (!file) return;
  const accepted = ['image/jpeg', 'image/png', 'image/jpg'];
  if (!accepted.includes(file.type)) {
    showError('Định dạng không hợp lệ. Vui lòng chọn ảnh JPG, JPEG hoặc PNG.');
    return;
  }
  if (file.size > 10 * 1024 * 1024) {
    showError('Ảnh quá lớn. Vui lòng chọn ảnh dưới 10 MB.');
    return;
  }

  selectedFile = file;
  if (previewUrl) URL.revokeObjectURL(previewUrl);
  previewUrl = URL.createObjectURL(file);
  previewImage.src = previewUrl;
  fileName.textContent = file.name;
  fileMeta.textContent = `${file.type.split('/')[1].toUpperCase()} · ${formatBytes(file.size)}`;
  uploadOptions.hidden = true;
  dropZone.hidden = true;
  previewArea.hidden = false;
  resultCard.hidden = true;
  setStep(2);
};

cameraButton.addEventListener('click', () => cameraInput.click());
uploadButton.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' || event.key === ' ') fileInput.click();
});
cameraInput.addEventListener('change', (event) => handleFile(event.target.files[0]));
fileInput.addEventListener('change', (event) => handleFile(event.target.files[0]));
chooseAgainButton.addEventListener('click', resetView);
resetButton.addEventListener('click', resetView);

['dragenter', 'dragover'].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.add('is-over');
  });
});
['dragleave', 'drop'].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.remove('is-over');
  });
});
dropZone.addEventListener('drop', (event) => handleFile(event.dataTransfer.files[0]));

classifyButton.addEventListener('click', async () => {
  if (!selectedFile) {
    showError('Vui lòng chọn ảnh trước khi phân loại.');
    return;
  }

  clearError();
  previewArea.hidden = true;
  loadingState.hidden = false;
  setStep(3);
  classifyButton.disabled = true;

  const formData = new FormData();
  formData.append('image', selectedFile);

  try {
    const response = await fetch('/api/classify', { method: 'POST', body: formData });
    const data = await response.json();
    if (!response.ok || !data.success) throw new Error(data.message || 'Không thể phân loại ảnh.');

    document.querySelector('#resultSymbol').textContent = data.icon || '♻';
    document.querySelector('#resultLabel').textContent = data.label.toUpperCase();
    document.querySelector('#confidenceValue').textContent = `${Number(data.confidence).toFixed(2)}%`;
    document.querySelector('#confidenceBar').style.width = `${Math.min(Number(data.confidence), 100)}%`;
    document.querySelector('#resultBin').textContent = data.bin;
    document.querySelector('#resultGuidance').textContent = data.guidance;
    document.querySelector('#fallbackNote').hidden = !data.is_fallback;
    loadingState.hidden = true;
    resultCard.hidden = false;
  } catch (error) {
    loadingState.hidden = true;
    previewArea.hidden = false;
    setStep(2);
    showError(error.message || 'Đã có lỗi xảy ra. Vui lòng thử lại.');
  } finally {
    classifyButton.disabled = false;
  }
});
