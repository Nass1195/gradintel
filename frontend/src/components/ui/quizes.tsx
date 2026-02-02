import { QuizQuestion } from "@/client/types.gen"

export default function Quizes(quizesQuestions: { quizQuestions: Array<QuizQuestion> }) {
    return (
        <div>
            
            <h2>Quizes Component</h2>
            <ul>
                {quizesQuestions.quizQuestions.map((question, index) => (
                    <li key={index}>{question.question}</li>
                ))}
            </ul>
        </div>
    )
}