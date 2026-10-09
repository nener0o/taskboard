console.log("--- Пример из методички ---");
console.log("gegegeg");
setTimeout(() => console.log("Step 1: In setTimeout"));
new Promise((resolve) => {
  console.log("Step 2: In promise constructor");
  resolve();
}).then(() => {
  console.log("Step 3: In then");
  setTimeout(() => console.log('Step 4: In setTimeout (inside of "then")'));
});
setTimeout(() => console.log("Step 5: In another setTimeout"));
console.log("tetete");

setTimeout(() => {
  console.log("--- Свой пример: микрозадачи внутри макрозадачи ---");
  console.log("Start");
  setTimeout(() => {
    console.log("A: таймер, макрозадача");
    Promise.resolve().then(() => console.log("B: микрозадача, поставленная внутри таймера"));
    queueMicrotask(() => console.log("B2: ещё одна микрозадача"));
    console.log("C: синхронный код того же таймера");
  });
  Promise.resolve()
    .then(() => console.log("P1: первый then"))
    .then(() => console.log("P2: второй then, цепочка промисов"));
  console.log("End");
});
