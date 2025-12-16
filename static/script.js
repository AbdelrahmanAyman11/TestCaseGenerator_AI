async function generate() {
  const story = document.getElementById("userStory").value;
  const output = document.getElementById("output");
  output.textContent = "Loading...";

  const response = await fetch("/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_story: story })
  });

  const data = await response.json();
  output.textContent = data.test_cases || data.error;
}
