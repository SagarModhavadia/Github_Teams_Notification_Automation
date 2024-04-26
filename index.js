const core = require("@actions/core");
const github = require("@actions/github");
const yaml = require("js-yaml");
const axios = require("axios");

try {
  const { getInput } = core;
  const {
    titleInput,
    jobStatusInput,
    lastCommitInput,
    sectionsInput,
    factsTitleInput,
    factsInput,
    webhookInput,
    buttonsInput,
    dry_runInput,
  } = {
    titleInput: getInput("title"),
    jobStatusInput: getInput("jobStatus"),
    lastCommitInput: getInput("lastCommit"),
    sectionsInput: getInput("sections"),
    factsTitle: getInput("factsTitle"),
    factsInput: getInput("facts"),
    webhookInput: getInput("webhook"),
    buttonsInput: getInput("buttons"),
    dry_runInput: getInput("dry_run"),
  };

  let stepsInput = core.getInput("steps");

  const { owner: repoOwner, repo: repoName } = github.context.repo;
  const { sha: commitSHA } = github.context;

  let json = {
    "@type": "MessageCard",
    "@context": "http://schema.org/extensions",
    summary:
      "MS Teams JSON Payload from GitHub Action https://github.com/sergioaten/msteams-notifications",
    sections: [],
    potentialAction: [],
  };

  var arrayJson = Array.from(Object.entries(json));
  const title = { title: titleInput };
  const themeColor = {
    themeColor: jobStatusInput === "success" ? "00FF00" : "FF0000",
  };
  arrayJson.splice(
    2,
    0,
    ...Object.entries(title),
    ...Object.entries(themeColor)
  );
  json = Object.fromEntries(arrayJson);

  if (sectionsInput) {
    json.sections = yaml.load(sectionsInput);
  } else {
    json.sections.push(
      { text: "<h1><strong>Changelog</strong></h1>" },
      {
        text: `Last commit: <a href="https://github.com/${repoOwner}/${repoName}/commit/${commitSHA}">${lastCommitInput}</a>`,
      }
    );

    if (factsInput) {
      const facts = yaml.load(factsInput);
      if (factsTitleInput) {
        const factsTitle = yaml.load(factsTitleInput);
        json.sections.push({ text: `<h1><strong>${factsTitle}</strong></h1>` });
      } else {
        json.sections.push({ text: "<h1><strong>Facts</strong></h1>" });
      }
      json.sections.push({
        facts: facts.map((fact) => {
          const name = Object.keys(fact)[0];
          return { name, value: fact[name] };
        }),
      });
    }

    if (stepsInput) {
      stepsInput = JSON.parse(stepsInput);
      const steps = Object.entries(stepsInput).map(([key, value]) => ({
        name: key,
        value: value.outcome
          .replace("success", "✅ OK")
          .replace("failure", "❌ FAIL")
          .replace("skipped", "🐇 SKIP"),
      }));
      json.sections.push({ text: "<h1><strong>Workflow Steps</strong></h1>" });
      json.sections.push({ facts: steps });
    }
  }

  if (buttonsInput) {
    const buttons = yaml.load(buttonsInput);
    json.potentialAction = buttons.map((button) => ({
      "@type": button.type,
      name: button.name,
      targets: button.targets,
    }));
  }

  if (dry_runInput !== "true") {
    axios
      .post(webhookInput, json, {
        headers: { "Content-Type": "application/json" },
      })
      .then((response) => {
        console.log("Request sent successfully");
        console.log("Response:", response.data);
      })
      .catch((error) => {
        console.error("Error sending request:", error);
      });
  } else {
    console.log("Dry run: yes. Not sending msg");
  }

  core.setOutput("jsonPayload", JSON.stringify(json, null, 2));
} catch (error) {
  core.setFailed(error.message);
}
