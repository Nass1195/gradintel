import { QuizQuestion } from "@/client/types.gen"
import { useState } from "react";


export default function QuizQuestionComponent( question : { question: QuizQuestion }) {
    const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);

    const getBorderColor = (option: string) => {

        if (selectedAnswer !== option) return "white";

    
        if (option === question.question.correct_answer) {
            return "green";
        }
        return "red";
    };
    
    return(
        <div>
            {question.question.question}

            <div style={{display: "flex", flexDirection: "row"}}>
                {question.question.options.map((option, index) => (
                    <div onClick={() => setSelectedAnswer(option)} 
                        style={{ 
                            border: `1px solid ${getBorderColor(option)}`, 
                            cursor: "pointer", 
                            borderRadius: "8px", 
                            margin: "4px", 
                            padding: "8px"}} 
                            onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")} 
                            onMouseEnter={(e) => (e.currentTarget.style.background = "#ffffff22")} 
                            key={index}>{option}</div>
                ))}
            </div>
        
        
        </div>
    )
}
