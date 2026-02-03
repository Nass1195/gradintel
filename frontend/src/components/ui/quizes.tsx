import { QuizQuestion } from "@/client/types.gen"
import QuizQuestionComponent from '@/components/ui/quizQuestion'

export default function Quizes(quizesQuestions: { quizQuestions: Array<QuizQuestion> }) {
    return (
        <div>
            
            <h2>Quizes Component</h2>
            <ul>
                {quizesQuestions.quizQuestions.map((question, index) => (
                    <QuizQuestionComponent  question={question} />
                ))}
            </ul>
        </div>
    )
}