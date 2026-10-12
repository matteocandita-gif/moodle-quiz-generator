// Prototipo "Javascript (con prompt)" - versione 2 (parametri: random, test_prima)

// Supporto prompt: ogni riga dello standard input è la risposta a un prompt()
const inputs = "{{ TEST.stdin | e('js') }}".split('\n');
let inputIndex = 0;
global.prompt = () => inputs[inputIndex++];

// Supporto random: sequenza fissa, sostituibile con il parametro "random".
// Il campo Extra del test indica la posizione da cui partire.
{% if QUESTION.parameters.random is defined and QUESTION.parameters.random %}
const randomValues = {{ QUESTION.parameters.random | json_encode }};
{% else %}
const randomValues = [ 0.15, 0.23, 0.52, 0.34, 0.75, 0.38, 0.62, 0.01, 0.29, 0.40, 0.92, 0.54, 0.42, 0.09, 0.10, 0.07, 0.88, 0.46, 0.01, 0.21, 0.17, 0.64, 0.06, 0.57, 0.25, 0.29, 0.81, 0.57, 0.02, 0.62, 0.03, 0.38, 0.64, 0.75, 0.22, 0.49, 0.89, 0.92, 0.13, 0.72 ];
{% endif %}
{% if TEST.extra is not empty %}
let randomIndex = {{ TEST.extra }} % randomValues.length;
{% else %}
let randomIndex = 0;
{% endif %}
Math.random = () => randomValues[randomIndex++ % randomValues.length];

var SEPARATOR = "#<ab@17943918#@>#";

{% if QUESTION.parameters.test_prima is defined and QUESTION.parameters.test_prima %}
{{ TEST.testcode }}

{{ STUDENT_ANSWER }}
{% else %}
{{ STUDENT_ANSWER }}

{{ TEST.testcode }}
{% endif %}
