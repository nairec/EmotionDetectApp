<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/github_username/repo_name">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">Emotion Detector App</h3>
    A web App designed for analysing the sentiments and emotions of different inputs
  <p align="center">
    <a href="https://github.com/nairec/EmotionDetectApp">View Repo</a>
    ·
    <a href="https://github.com/nairec/EmotionDetectApp/issues">Report Bug</a>
    ·
    <a href="https://github.com/nairec/EmotionDetectApp/issues">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#In-work">In-work Features</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com)

EmotionDetectApp, as the name implies, is a web app developed for analysing the sentiment and emotion of different kinds of inputs
Features:
<ul>
    <li>text analysis</li>
    <li>tweets analysis</li>
    <li>youtube comments analysis</li>
    <li>file text analysis</li>
</ul>
This software is developed with roBERTa and emoRoBERTa models of huggingface

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

<ul>
    <li>Flask</li>
</ul>

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

The following text will guide you setting up the environment for using the app on your local machine

### Prerequisites

install all the requirements listed in requirements.txt in the same directory of the app
```sh
pip install -r requirements.txt 
```

### Installation

If you want to use the youtube comments feature, you will need to get an API Key
1. Get a free API Key at https://console.cloud.google.com/welcome starting a new project
2. Clone the repo
   ```sh
   git clone https://github.com/nairec/EmotionDetectApp.git
   ```
3. Enter your API in `.env`
   ```
   YOUTUBE_API_KEY = 'ENTER YOUR API';
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- In-work -->
## In-work features

- [ ] Exporting datao utput as CSV
- [ ] Graphics as output visualization

See the [open issues](https://github.com/nairec/EmotionDetectApp/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

This is one of my first projects, so if you have any suggestion, i would deeply thank you for crating a pull request, or simply open an issue.
Also, don't forget to give the project a star!

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

email - irecgc@gmail.com

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<p align="right">(<a href="#readme-top">back to top</a>)</p>
