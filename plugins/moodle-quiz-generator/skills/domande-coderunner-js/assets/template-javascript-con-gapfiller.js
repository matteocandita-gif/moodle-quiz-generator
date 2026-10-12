// Prototipo "Javascript (con gapfiller)" - con random per test (Extra) e parametro random
//Supporto Prompt
let inputs = `{{ TEST.stdin }}`.split('\n')
let inputIndex = 0
global.prompt = () => inputs[inputIndex++]

//Supporto Random
{% if QUESTION.parameters.random is defined and QUESTION.parameters.random %}
const randomValues = {{ QUESTION.parameters.random | json_encode }};
{% else %}
const randomValues = [ 0.15, 0.23, 0.52, 0.34, 0.75, 0.38, 0.62, 0.01, 0.29, 0.40, 0.92, 0.54, 0.42, 0.09, 0.10, 0.07, 0.88, 0.46, 0.01, 0.21,  0.17, 0.64, 0.06, 0.57, 0.25, 0.29, 0.81, 0.57, 0.02, 0.62,0.03, 0.38, 0.64, 0.75, 0.22, 0.49, 0.89, 0.92, 0.13, 0.72 ];
{% endif %}
let randomIndex = 0  ;  // Offset dipendente dall'indice del test case
Math.random = () => randomValues[randomIndex++ % randomValues.length];

let SEPARATOR = "#<ab@17943918#@>#";
let code= "{{ QUESTION.globalextra | e('js')}}";//Prendiamo il test scritto in Global Extra contenente i GAP
let field_values = {{ STUDENT_ANSWER}}; //Prendiamo le risposte dello studente

const regex = /\{\[.*?\]\}/;//Questa prende {[___]} ovvero i GAP

for (let field of field_values) {//Inseriamo le risposte dello studente nei GAP
    code = code.replace(regex, field);
}

let tests = {{ TESTCASES | json_encode }};
for (let i=0;i<tests.length;i++) {//Per ogni test, anteponiamo il testo del test al codice effettivo.
    let test=tests[i];
    let testcode = test['testcode'];
    let finalcode=testcode+"\n"+ code;
    
    inputs=test['stdin'].split('\n');
    inputIndex=0;
    randomIndex = (parseInt(test['extra']) || 0) % randomValues.length;
    eval(finalcode);
    if(i<tests.length-1){//Questo permette di dividere il flusso dell'output nel caso di più test. Divide l'output uno in ogni test case
        process.stdout.write(SEPARATOR + "\n");
    }
}
