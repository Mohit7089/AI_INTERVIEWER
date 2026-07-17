import fs from "fs"
import { askAi } from "../services/openRouter.service.js";
import User from "../models/user.model.js";
import Interview from "../models/interview.model.js";
import axios from "axios";
import FormData from "form-data";

const callResumeAnalyzer = async (filePath) => {
  const formData = new FormData();

  formData.append("file", fs.createReadStream(filePath));

  const res = await axios.post(
    "http://127.0.0.1:5000/analyze", // Flask API
    formData,
    {
      headers: formData.getHeaders(),
    }
  );

  return res.data;
};

export const analyzeResume = async (req, res) => {
  try {
    // ✅ check file
    if (!req.file) {
      return res.status(400).json({ message: "Resume required" });
    }

    const filepath = req.file.path;

    // ✅ call Flask API
    const result = await callResumeAnalyzer(filepath);

    const resumeText = result.resumeText;

    // 🔥 LLM call for project extraction
const safeText = resumeText?.slice(0, 2000);
if (!resumeText || resumeText.trim().length < 50) {
  console.log("❌ Resume text is empty or too short");

  return res.status(400).json({
    message: "Resume text extraction failed"
  });
}

const aiResponse = await askAi([
  {
    role: "system",
    content: `
You are an AI that extracts projects from resumes.

Extract ONLY top 3 projects.
If no projects found, return empty array [].

Return strictly JSON:
[
  {
    "project_name": "...",
    "summary": "..."
  }
]
`
  },
  {
    role: "user",
    content: safeText
  }
]);
    console.log("🔥 Flask Response:", result);
    console.log("🤖 AI Response:", aiResponse);

    // ✅ safe delete file
    if (fs.existsSync(filepath)) {
      fs.unlinkSync(filepath);
    }

    // ✅ extract role
    const role = result.roles?.[0]?.[0]?.toUpperCase() || "DEVELOPER";

    // 🔥 PROJECTS FROM LLM (with fallback)
    let projects = [];

    try {
      if (!aiResponse || !aiResponse.trim()) {
        throw new Error("Empty AI response");
      }

      const clean = aiResponse.replace(/```json|```/g, "").trim();
      const parsed = JSON.parse(clean);

      projects = parsed.map(p => ({
        name: p.project_name,
        description: p.summary
      }));

    } catch (err) {
      console.log("⚠️ LLM failed, fallback to Flask");

      projects = (result.projects || []).map(p => ({
        name: p.project_name,
        description: p.summary
      }));
    }

    // ✅ clean + sort skills
    const skills = (result.skills || [])
      .map((s) => s.toUpperCase())
      .sort();

    // ✅ clean + sort soft skills
    const softSkills = (result.soft_skills || [])
      .map((s) => s.toUpperCase())
      .sort();

    // ✅ final response
    return res.json({
      role,
      experience: "",
      projects,        // ✅ from LLM
      skills,
      softSkills,
      score: result.score || 0,
    });

  } catch (error) {
    console.error(error);

    // ✅ safe cleanup if error
    if (req.file && fs.existsSync(req.file.path)) {
      fs.unlinkSync(req.file.path);
    }

    return res.status(500).json({ message: error.message });
  }
};

export const generateQuestion = async (req, res) => {
  try {
    let { role, experience, mode, resumeText, projects, skills } = req.body

    role = role?.trim();
    experience = experience?.trim();
    mode = mode?.trim();

    if (!role || !experience || !mode) {
      return res.status(400).json({ message: "Role, Experience and Mode are required." })
    }

    const user = await User.findById(req.userId)

    if (!user) {
      return res.status(404).json({
        message: "User not found."
      });
    }

    // if (user.credits < 50) {
    //   return res.status(400).json({
    //     message: "Not enough credits. Minimum 50 required."
    //   });
    // }

    const projectText = Array.isArray(projects) && projects.length
      ? projects.join(", ")
      : "None";

    const skillsText = Array.isArray(skills) && skills.length
      ? skills.join(", ")
      : "None";

    const safeResume = resumeText?.trim() || "None";

    const userPrompt = `
    Role:${role}
    Experience:${experience}
    InterviewMode:${mode}
    Projects:${projectText}
    Skills:${skillsText},
    Resume:${safeResume}
    `;

    if (!userPrompt.trim()) {
      return res.status(400).json({
        message: "Prompt content is empty."
      });
    }

    const messages = [

      {
        role: "system",
        content: `
You are a real human interviewer conducting a professional interview.

Speak in simple, natural English as if you are directly talking to the candidate.

Generate exactly 5 interview questions.

Strict Rules:
- ask technical question
- Each question must contain between 15 and 25 words.
- Each question must be a single complete sentence.
- Do NOT number them.
- Do NOT add explanations.
- Do NOT add extra text before or after.
- One question per line only.
- Keep language simple and conversational.
- Questions must feel practical and realistic.

Difficulty progression:
Question 1 → easy  
Question 2 → easy  
Question 3 → medium  
Question 4 → medium  
Question 5 → hard  

Make questions based on the candidate’s role, experience,interviewMode, projects, skills, and resume details.
`
      }
      ,
      {
        role: "user",
        content: userPrompt
      }
    ];


    const aiResponse = await askAi(messages)

    if (!aiResponse || !aiResponse.trim()) {
           
      return res.status(500).json({
        message: "AI returned empty response."
      });

    }

    const questionsArray = aiResponse
      .split("\n")
      .map(q => q.trim())
      .filter(q => q.length > 0)
      .slice(0, 5);

    if (questionsArray.length === 0) {
      
      return res.status(500).json({
        message: "AI failed to generate questions."
      });
    }

    user.credits -= 50;
    await user.save();

    const interview = await Interview.create({
      userId: user._id,
      role,
      experience,
      mode,
      resumeText: safeResume,
      questions: questionsArray.map((q, index) => ({
        question: q,
        difficulty: ["easy", "easy", "medium", "medium", "hard"][index],
        timeLimit: [60, 60, 90, 90, 120][index],
      }))
    })

    res.json({
      interviewId: interview._id,
      creditsLeft: user.credits,
      userName: user.name,
      questions: interview.questions
    });
  } catch (error) {
    return res.status(500).json({message:`failed to create interview ${error}`})
  }
}


// export const submitAnswer = async (req, res) => {
//   try {
//     const { interviewId, questionIndex, answer, timeTaken } = req.body

//     const interview = await Interview.findById(interviewId)
//     const question = interview.questions[questionIndex]

//     // If no answer
//     if (!answer) {
//       question.score = 0;
//       question.feedback = "You did not submit an answer.";
//       question.answer = "";

//       await interview.save();

//       return res.json({
//         feedback: question.feedback
//       });
//     }

//     // If time exceeded
//     if (timeTaken > question.timeLimit) {
//       question.score = 0;
//       question.feedback = "Time limit exceeded. Answer not evaluated.";
//       question.answer = answer;

//       await interview.save();

//       return res.json({
//         feedback: question.feedback
//       });
//     }


//     const messages = [
//       {
//         role: "system",
//         content: `
// You are a professional human interviewer evaluating a candidate's answer in a real interview.

// Evaluate naturally and fairly, like a real person would.

// Score the answer in these areas (0 to 10):

// 1. Confidence – Does the answer sound clear, confident, and well-presented?
// 2. Communication – Is the language simple, clear, and easy to understand?
// 3. Correctness – Is the answer accurate, relevant, and complete?

// Rules:
// - Be realistic and unbiased.
// - Do not give random high scores.
// - If the answer is weak, score low.
// - If the answer is strong and detailed, score high.
// - Consider clarity, structure, and relevance.

// Calculate:
// finalScore = average of confidence, communication, and correctness (rounded to nearest whole number).

// Feedback Rules:
// - Write natural human feedback.
// - 10 to 15 words only.
// - Sound like real interview feedback.
// - Can suggest improvement if needed.
// - Do NOT repeat the question.
// - Do NOT explain scoring.
// - Keep tone professional and honest.

// Return ONLY valid JSON in this format:

// {
//   "confidence": number,
//   "communication": number,
//   "correctness": number,
//   "finalScore": number,
//   "feedback": "short human feedback"
// }
// `
//       }
//       ,
//       {
//         role: "user",
//         content: `
// Question: ${question.question}
// Answer: ${answer}
// `
//       }
//     ];


//     const aiResponse = await askAi(messages)


//     const parsed = JSON.parse(aiResponse);

//     question.answer = answer;
//     question.confidence = parsed.confidence;
//     question.communication = parsed.communication;
//     question.correctness = parsed.correctness;
//     question.score = parsed.finalScore;
//     question.feedback = parsed.feedback;
//     await interview.save();


//     return res.status(200).json({feedback :parsed.feedback})
//   } catch (error) {
//     return res.status(500).json({message:`failed to submit answer ${error}`})

//   }
// }


export const submitAnswer = async (req, res) => {
  try {
    const { interviewId, question, answer, timeTaken, keywords } = req.body;

    const interview = await Interview.findById(interviewId);

    const dbQuestion = interview.questions.find(
  q => q.question.trim() === question.trim()
);

    if (!answer) {
      return res.json({
        score: 0,
        feedback: "You did not submit an answer."
      });
    }

    if (timeTaken > 60) {
      return res.json({
        score: 0,
        feedback: "Time limit exceeded."
      });
    }

   const prompt = `
Evaluate this interview answer out of 10.

Question: ${question}
Answer: ${answer}

Be fair. Consider:
- correctness
- clarity
- depth

Return JSON:
{
  "score": number,
  "feedback": "text"
}
`;

const aiResponse = await askAi([
  { role: "user", content: prompt }
]);

const parsed = JSON.parse(aiResponse);

const result = {
  score: parsed.score,
  feedback: parsed.feedback
};

    const feedbackPrompt = `
Give short interview feedback (1 sentence):

Question: ${question}
Answer: ${answer}
`;

    const aiFeedback = await askAi([
      { role: "user", content: feedbackPrompt }
    ]);

    const followUpPrompt = `
Based on this answer:

"${answer}"

Ask ONE follow-up interview question.
`;

    const nextQuestion = await askAi([
      { role: "user", content: followUpPrompt }
    ]);

    // ✅ SAVE TO DB
    if (dbQuestion) {
      dbQuestion.answer = answer;
      dbQuestion.score = result.score;
      dbQuestion.feedback = result.feedback;

      dbQuestion.confidence = result.score;
      dbQuestion.communication = result.score;
      dbQuestion.correctness = result.score;
    }



    await interview.save();

    return res.status(200).json({
      feedback: aiFeedback,
      score: result.score,
      nextQuestion
    });

  } catch (error) {
    console.log("🔥 ERROR:", error);
    return res.status(500).json({
      message: `failed to submit answer ${error}`
    });
  }
};


export const finishInterview = async (req, res) => {
  try {
    const { interviewId } = req.body;

    const interview = await Interview.findById(interviewId);

    const questions = interview.questions;

    // ✅ calculate scores
    let total = 0;
    let confidence = 0;
    let communication = 0;
    let correctness = 0;

    questions.forEach(q => {
      total += q.score || 0;
      confidence += q.confidence || 0;
      communication += q.communication || 0;
      correctness += q.correctness || 0;
    });

    const finalScore = (total / questions.length).toFixed(1);

    // ✅ average skills
    confidence = Math.round(confidence / questions.length);
    communication = Math.round(communication / questions.length);
    correctness = Math.round(correctness / questions.length);

    // ✅ format for frontend
    const questionWiseScore = questions.map(q => ({
      question: q.question,
      score: q.score,
      feedback: q.feedback
    }));

    // ✅ save
    interview.finalScore = finalScore;
    await interview.save();

    // ✅ RESPONSE MATCHING YOUR UI
    return res.json({
      finalScore,
      confidence,
      communication,
      correctness,
      questionWiseScore
    });

  } catch (error) {
    console.log(error);
    res.status(500).json({ message: error.message });
  }
};


export const getMyInterviews = async (req,res) => {
  try {
    const interviews = await Interview.find({userId:req.userId})
    .sort({ createdAt: -1 })
    .select("role experience mode finalScore status createdAt");

    return res.status(200).json(interviews)

  } catch (error) {
     return res.status(500).json({message:`failed to find currentUser Interview ${error}`})
  }
}

export const getInterviewReport = async (req,res) => {
  try {
    const interview = await Interview.findById(req.params.id)

    if (!interview) {
      return res.status(404).json({ message: "Interview not found" });
    }


    const totalQuestions = interview.questions.length;

    let totalConfidence = 0;
    let totalCommunication = 0;
    let totalCorrectness = 0;

    interview.questions.forEach((q) => {
      totalConfidence += q.confidence || 0;
      totalCommunication += q.communication || 0;
      totalCorrectness += q.correctness || 0;
    });
    const avgConfidence = totalQuestions
      ? totalConfidence / totalQuestions
      : 0;

    const avgCommunication = totalQuestions
      ? totalCommunication / totalQuestions
      : 0;

    const avgCorrectness = totalQuestions
      ? totalCorrectness / totalQuestions
      : 0;

       return res.json({
      finalScore: interview.finalScore,
      confidence: Number(avgConfidence.toFixed(1)),
      communication: Number(avgCommunication.toFixed(1)),
      correctness: Number(avgCorrectness.toFixed(1)),
      questionWiseScore: interview.questions
    });

  } catch (error) {
    return res.status(500).json({message:`failed to find currentUser Interview report ${error}`})
  }
}




