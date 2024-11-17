document.addEventListener("DOMContentLoaded", () => {
  const binaryImage = document.getElementById("binaryImage");
  const emptySpaces = document.getElementById("emptySpaces");
  const countdown = document.getElementById("countdown");

  let currentBinaryValue = ""; // Almacena el valor binario actual
  let updateInterval = 10; // Intervalo de actualización en segundos

  function fetchAndUpdateImage() {
    fetch("https://api.thingspeak.com/channels/2747991/fields/1.json?api_key=X2KNF2B4PBS0L14R&results=1")
      .then(response => response.json())
      .then(data => {
        const feeds = data.feeds;
        if (feeds && feeds.length > 0) {
          const newBinaryValue = feeds[0].field1;

          if (newBinaryValue !== currentBinaryValue) {
            currentBinaryValue = newBinaryValue;

            // Actualiza la imagen si el valor binario cambia
            const imageUrl = `${currentBinaryValue}.png`;
            binaryImage.src = imageUrl;

            // Cuenta los ceros en el valor binario para calcular espacios vacíos
            const vacantSpaces = (currentBinaryValue.match(/0/g) || []).length;
            emptySpaces.textContent = `Espacios vacíos: ${vacantSpaces}`;
          }
        }
      })
      .catch(error => console.error("Error fetching data:", error));
  }

  function startCountdown() {
    let remainingTime = updateInterval;
    countdown.textContent = `Próxima actualización en: ${remainingTime}s`;

    const timer = setInterval(() => {
      remainingTime -= 1;
      countdown.textContent = `Próxima actualización en: ${remainingTime}s`;

      if (remainingTime <= 0) {
        clearInterval(timer);
        fetchAndUpdateImage(); // Actualiza cuando la cuenta regresiva termina
        startCountdown(); // Reinicia la cuenta regresiva
      }
    }, 1000);
  }

  fetchAndUpdateImage(); // Llama por primera vez
  startCountdown(); // Inicia la cuenta regresiva
});
