# 🤝 Contributing to ESP32 Display Simulator

We warmly welcome and appreciate all contributions! Whether you're reporting a bug, suggesting a feature, or submitting code, your help is valuable. By contributing, you agree that your submissions will be licensed under the project's **MIT License**.

***

## ⚙️ Setting Up Your Development Environment

Since this project is built using **Python** and the standard library module **Tkinter**, setup is quick. Using a Virtual Environment (`venv`) is strongly recommended to keep dependencies isolated.

1.  **Fork the Repository:** Click the "Fork" button at the top right of the repository page on GitHub.
2.  **Clone Your Fork:**
    ```bash
    git clone [https://github.com/Heavendart888/Esp32_display_simulator.git](https://github.com/Heavendart888/Esp32_display_simulator.git)
    cd Esp32_display_simulator
    ```
3.  **Create and Activate a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    
    # Activate:
    # macOS/Linux: source venv/bin/activate
    # Windows (PowerShell): .\venv\Scripts\Activate.ps1
    # Windows (CMD): venv\Scripts\activate
    ```
4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Run the Project:**
    ```bash
    python designer.py
    ```

***

## 🐛 Reporting Bugs

If you encounter an error, crash, or unexpected behavior, please let us know:

1.  Check the existing **Issues** to see if the bug has already been reported.
2.  If not, open a new **Issue**.
3.  Include a **clear title** and a detailed description.
4.  Provide **steps to reproduce** the bug (e.g., "Select 128x64 display, add a Rect, drag it out of bounds...").
5.  Specify your **Operating System** and **Python Version**.

***

## ✨ Suggesting Enhancements

We are always looking for ways to improve the simulator's functionality and user experience:

1.  Check the existing **Issues** and **Pull Requests** for similar suggestions.
2.  Open a new **Issue** with the tag **`enhancement`**.
3.  Clearly describe the feature and explain why it would be useful.

***

## 💻 Submitting Code Changes (Pull Requests)

Follow these steps to ensure a smooth review process:

1.  **Branch:** Create a new branch for your changes (e.g., `git checkout -b feature/new-fill-color` or `git checkout -b bugfix/fix-resize-clamp`).
2.  **Commit:** Write clear, descriptive commit messages. Focus each commit on a single logical change.
3.  **Testing:** Manually test your changes to ensure they work as expected and do not break existing functionality.
4.  **Pull Request (PR):**
    * Push your branch to your fork.
    * Open a Pull Request against the `main` branch of the original repository.
    * In the PR description, reference any related issues (e.g., `Fixes #123`).
    * Keep the **PR focused**. Large, complex changes should be broken down if possible.