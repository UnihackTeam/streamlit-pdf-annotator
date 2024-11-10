<template>
  <div style="padding-top: 20px; height: 1200px">
    <span>
      Num pages: {{ numPages }} | Current page: 
      <!--<input 
        type="number" 
        min="1" 
        :max="numPages" 
        :value="currentPage"
        @input="handleInput"
        style="padding: 0.25rem 0.75rem;
          border-radius: 0.5rem;
          min-height: 2.5rem;
          margin: 0px;
          line-height: 1.6;
          outline: none;
          font-size: 16px;
          color: inherit;
          background-color: rgb(255, 255, 255);
          border: 1px solid rgba(49, 51, 63, 0.2);"
      > --> {{ currentPage }} &nbsp;
      <!--<button @click="onClicked">Click Me!</button>-->
    </span>
    <div style="width: 100%; display: flex; flex-direction: row; justify-content: space-between; margin-top: 10px;">
      <button 
        :disabled="currentPage == 1"
        class="button" 
        @click="goTo(-1)"
      >
        Go to previous page
      </button>
      <button 
        :disabled="currentPage == numPages"
        class="button"
        @click="goTo(1)"
      >
        Go to next page
      </button>
    </div>
    <div style="margin-top: 10px; border-radius: 0.5rem; border: 1px solid rgba(49, 51, 63, 0.2); overflow: hidden;">
      <canvas ref="pdfCanvas" @click="createQuestion"></canvas>
      <div 
        v-for="question in questions" 
        :key="question.id"
        class="question"
        :style="{left: (canvasRect.left + question.x) + 'px', top: (canvasRect.top + question.y) + 'px'}"
      >
        <div 
          v-show="question.page == currentPage"
          @click="question.isOpen = !question.isOpen" 
          class="toggle"
        >
          <span style="width: 20px; height: 20px; font-size: 18px;">★</span>
        </div>
        <div v-show="question.isOpen" class="popup">
          <div>
            <input v-if="!user.is_teacher" type="text" placeholder="Here goes your question" v-model="question.question">
            <p v-if="user.is_teacher" style="margin: 0;">{{ question.question }}</p>
            <button
              v-if="!user.is_teacher"
              class="button" 
              style="background-color: #FF4500; color: white; margin-left: 10px;" @click="removeQuestion(question.id)"
            >
              Remove
            </button>
          </div>
          <input v-if="user.is_teacher" type="text" placeholder="Here goes your reply" v-model="question.answer">
          <button v-if="!user.is_teacher" class="button blue" style="margin-top: 10px;" @click="askQuestion(question.id, question.question); question.isOpen = false">Ask question</button>
          <button v-if="user.is_teacher" class="button blue" style="margin-top: 10px; margin-left: 10px;" @click="question.isOpen = false">Reply</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from "vue"
import { Streamlit } from "streamlit-component-lib"
import { useStreamlit } from "./streamlit"
import { createClient } from '@supabase/supabase-js'

export default {
  name: "Annotator",
  props: ["args"], // Arguments that are passed to the plugin in Python are accessible in prop "args"
  setup(props) {
    useStreamlit() // lifecycle hooks for automatic Streamlit resize

    const numPages = ref(0);
    const currentPage = ref(1);
    const questions = ref([]);
    const inputNumberRef = ref(null);
    const canvasRect = ref({left:0, top:0});
    const user = ref();
    let pdfDoc = null;

    // Create a single supabase client for interacting with your database
    let supabase = null;
    let userId = null;
    let docId = null;
    let supabaseUrl = null;
    let supabaseKey = null;

    onMounted(async () => {
      const args = props.args.doc;
      userId = args.user_id;
      docId = args.doc_id;
      supabaseUrl = args.supabase_url;
      supabaseKey = args.supabase_key;
      
      supabase = createClient(supabaseUrl, supabaseKey);

      // Get user
      const { data: userData, error: userError } = await supabase
        .from('users')
        .select()
        .eq('id', userId);
      if (userError == null) {
        user.value = userData[0];
        console.log('User data');
        console.log(user.value);
        setTimeout(() => {
          user.value.is_teacher = true
          console.log('NOw is teacher');
          console.log(user.value);
        }, 30000);
      }

      // Get document
      const { data: docData, error: docError } = await supabase
        .from('docs')
        .select()
        .eq('id', docId);
      
      const document = docData[0];
      const documentPath = document.file_path;

      // Get questions
      const { data: questionsData, error: questionsError } = await supabase
        .from('questions')
        .select()
        .eq('doc', docId);

      if (questionsError == null) {
        questions.value = questionsData;
      }

      await loadPdf(documentPath);
    });

    const pdfCanvas = ref(null);

    async function loadPdf(url) {
      // Dynamically import PDF.js from the CDN
      const pdfjsLib = await import('https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.8.69/pdf.min.mjs');
      
      // Load the PDF worker from the CDN
      pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.8.69/pdf.worker.min.mjs';

      // Decode Base64
      //const pdfData = atob(base64Pdf);

      // Load the PDF document
      //pdfDoc = await pdfjsLib.getDocument({ data: pdfData }).promise;
      pdfDoc = await pdfjsLib.getDocument(url).promise;
      console.log(pdfDoc);

      numPages.value = pdfDoc._pdfInfo.numPages;
      Streamlit.setComponentValue(numPages.value);

      await renderPage();
    }

    async function renderPage() {
      // Get the first page
      const page = await pdfDoc.getPage(currentPage.value);

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

      // Get the canvas's position relative to the page
      canvasRect.value = pdfCanvas.value.getBoundingClientRect();
    }

    async function goTo(number) {
      currentPage.value += number;
      await renderPage();
    }

    /*async function handleInput(event) {
      currentPage.value = event.target.value;
      console.log('pageChanged to ' + currentPage.value);
      await renderPage();
    }

    watch(currentPage, (newPage) => {
      if (inputNumberRef.value) {
        inputNumberRef.value.value = newPage;
      }
    });*/

    async function createQuestion(event) {
      // Calculate click coordinates relative to the canvas
      const x = event.clientX - canvasRect.value.left;
      const y = event.clientY - canvasRect.value.top;

      // Close any open question
      questions.value.forEach(item => item.isOpen = false);

      // Create a new question and show it
      const { data, error } = await supabase
        .from('questions')
        .insert({
          doc: docId,
          asked_by: userId,
          question: '',
          answer: '',
          page: currentPage.value,
          x: x,
          y: y
        })
        .select();

      if (error == null) {
        data[0].isOpen = true;
        questions.value.push(data[0]);
      }
    }

    async function askQuestion(questionId, question) {
      const { error } = await supabase
        .from('questions')
        .update({ question: question })
        .eq('id', questionId)
    }

    async function removeQuestion(questionId) {
      const response = await supabase
        .from('questions')
        .delete()
        .eq('id', questionId);

      // Remove question locally
      const index = questions.value.findIndex(item => item.id === questionId);
      if (index !== -1) {
        questions.value.splice(index, 1);
      }
    }

    return {
      numPages,
      currentPage,
      pdfCanvas,
      questions,
      canvasRect,
      inputNumberRef,
      user,
      goTo,
      //handleInput,
      createQuestion,
      askQuestion,
      removeQuestion,
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

.button.blue {
  background-color: #1E90FF; 
  color: white;
}
.button.blue:hover {
  background-color: #1E90FF; 
  border: 1px solid #1E90FF;
  color: white;
}

.question {
  position: absolute;
  display: flex;
  flex-direction: row;
}

.question .toggle {
  max-height: 21px;
  max-width: 37px;
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

.question .popup input {
  padding: 0rem 0.4rem;
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
  outline: none;
}
</style>