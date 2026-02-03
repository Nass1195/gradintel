import { QuizQuestion } from "@/client/types.gen"


export default function QuizQuestionComponent( question : { question: QuizQuestion }) {
    return(
        <div>
            {question.question.question}

            <div style={{display: "flex", flexDirection: "row"}}>
                {question.question.options.map((option, index) => (
                    <div style={{ border: "1px solid white", backgroundColor: "red"}} key={index}>{option}</div>
                ))}
            </div>
        
        
        </div>
    )
}
