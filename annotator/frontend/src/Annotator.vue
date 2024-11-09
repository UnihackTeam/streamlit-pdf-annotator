<template>
  <div style="height: 1200px">
    <span>
      Num pages: {{ numPages }} | Current page: {{ currentPage + 1 }} &nbsp;
      <!--<button @click="onClicked">Click Me!</button>-->
    </span>
    <div style="width: 100%; display: flex; flex-direction: row; justify-content: space-between; margin-top: 10px;">
      <button 
        :disabled="currentPage == 0"
        class="button" 
        @click="goTo(-1)"
      >
        Go to previous page
      </button>
      <button 
        :disabled="currentPage == (numPages - 1)"
        class="button"
        @click="goTo(1)"
      >
        Go to next page
      </button>
    </div>
    <div style="margin-top: 10px; border-radius: 0.5rem; border: 1px solid rgba(49, 51, 63, 0.2); overflow: hidden;">
      <canvas ref="pdfCanvas" @click="openQuestion"></canvas>
      <div 
        v-for="question in questions" 
        class="question"
        :style="{left: (canvasRect.left + question.position.x) + 'px', top: (canvasRect.top + question.position.y) + 'px'}"
      >
        <div 
          v-show="question.position.page == currentPage"
          @click="question.isOpen = !question.isOpen" 
          class="toggle"
        >
          <span style="width: 20px; height: 20px; font-size: 18px;">★</span>
        </div>
        <div v-show="question.isOpen" class="popup">
          <input type="text" placeholder="Here goes your question">
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue"
import { Streamlit } from "streamlit-component-lib"
import { useStreamlit } from "./streamlit"

export default {
  name: "Annotator",
  props: ["args"], // Arguments that are passed to the plugin in Python are accessible in prop "args"
  setup(props) {
    useStreamlit() // lifecycle hooks for automatic Streamlit resize

    const numPages = ref(0);
    const currentPage = ref(0);
    let pdfDoc = null;

    onMounted(() => {
      loadPdf(props.args.doc);
      //console.log(props.args.doc);
    });

    const pdfCanvas = ref(null);

    async function loadPdf(base64Pdf) {
      // Dynamically import PDF.js from the CDN
      const pdfjsLib = await import('https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.8.69/pdf.min.mjs');
      
      // Load the PDF worker from the CDN
      pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.8.69/pdf.worker.min.mjs';

      // Decode Base64
      const pdfData = atob(base64Pdf);

      // Load the PDF document
      pdfDoc = await pdfjsLib.getDocument({ data: pdfData }).promise;
      console.log(pdfDoc);

      numPages.value = pdfDoc._pdfInfo.numPages;
      Streamlit.setComponentValue(numPages.value);

      await renderPage();
    }

    async function renderPage() {
      // Get the first page
      const page = await pdfDoc.getPage(currentPage.value + 1);

      // Set up canvas context
      //const canvas = this.$refs.pdfCanvas;
      const context = pdfCanvas.value.getContext('2d');

      // Define the desired canvas width
      const canvasWidth = 704;

      // Calculate the scale to fit the width
      const viewport = page.getViewport({ scale: 1 });
      const scale = canvasWidth / viewport.width;
      const scaledViewport = page.getViewport({ scale });

      // Adjust canvas dimensions
      pdfCanvas.value.width = canvasWidth;
      pdfCanvas.value.height = scaledViewport.height;

      // Render the PDF page into the canvas
      await page.render({
        canvasContext: context,
        viewport: scaledViewport,
      }).promise;
    }

    async function goTo(number) {
      currentPage.value += number;
      await renderPage();
    }

    const popup = ref(null);
    const questions = ref([]);
    const canvasRect = ref(null);
    function openQuestion(event) {
      // Get the canvas's position relative to the page
      canvasRect.value = pdfCanvas.value.getBoundingClientRect();
        
      // Calculate click coordinates relative to the canvas
      const x = event.clientX - canvasRect.value.left;
      const y = event.clientY - canvasRect.value.top;
      
      // Position the popup and make it visible
      /*popup.value.style.left = `${canvasRect.value.left + x}px`;
      popup.value.style.top = `${canvasRect.value.top + y}px`;
      popup.value.style.display = 'block';*/

      // Close any open question
      questions.value.forEach(item => item.isOpen = false);

      // Create a new question and show it
      questions.value.push({
        position: {
          page: currentPage.value,
          x: x,
          y: y,
        },
        question: '',
        reply: '',
        isOpen: true
      });
      console.log(questions.value);
    }

    return {
      numPages,
      currentPage,
      pdfCanvas,
      questions,
      canvasRect,
      popup,
      goTo,
      openQuestion,
    }
  },
}
</script>

<style>
.button {
  display: inline-flex;
  -moz-box-align: center;
  align-items: center;
  -moz-box-pack: center;
  justify-content: center;
  font-weight: 400;
  padding: 0.25rem 0.75rem;
  border-radius: 0.5rem;
  min-height: 2.5rem;
  margin: 0px;
  line-height: 1.6;
  color: inherit;
  width: auto;
  cursor: pointer;
  user-select: none;
  background-color: rgb(255, 255, 255);
  border: 1px solid rgba(49, 51, 63, 0.2);
}

.button:hover {
  border-color: rgb(255, 75, 75);
  color: rgb(255, 75, 75);
}

.button:active {
  color: rgb(255, 255, 255);
  border-color: rgb(255, 75, 75);
  background-color: rgb(255, 75, 75);
}

.button:disabled {
  color: #b2b2b2;
}

.button:disabled:hover {
  color: #b2b2b2;
  border: 1px solid rgba(49, 51, 63, 0.2);
}

.button:disabled:active {
  color: #b2b2b2;
  border: 1px solid rgba(49, 51, 63, 0.2);
  background-color: rgb(255, 255, 255);
}

.question {
  position: absolute;
  display: flex;
  flex-direction: row;
}

.question .toggle {
  border-radius: 0.5rem;
  border: 1px solid rgba(49, 51, 63, 0.2);
  color: #f5b041;
  padding: 10px;
  background-color: white;
  user-select: none; 
  cursor: pointer;
}

.question .popup {
  margin-left: 5px;
  z-index: 10;
  border-radius: 0.5rem;
  border: 1px solid rgba(49, 51, 63, 0.2);
  padding: 10px;
  background-color: white;
}
</style>