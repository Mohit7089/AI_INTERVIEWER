// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import {getAuth, GoogleAuthProvider} from "firebase/auth";

// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCMBaBFOMVZil58ZI9QBmChBgNtWX8ipQE",
  authDomain: "ai-interviewer-f54fc.firebaseapp.com",
  projectId: "ai-interviewer-f54fc",
  storageBucket: "ai-interviewer-f54fc.firebasestorage.app",
  messagingSenderId: "764383288868",
  appId: "1:764383288868:web:8a4ad49a1f7462afefc2b1",
  measurementId: "G-C6L4XGM81Z"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

const auth=getAuth(app);

const provider=new GoogleAuthProvider();

export {auth, provider};