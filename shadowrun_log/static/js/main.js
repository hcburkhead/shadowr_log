// main.js

document.addEventListener("DOMContentLoaded", function () {
    // Determine if Unix Mode is enabled
    const isUnixMode = unixModeEnabled === 'true';

    if (isUnixMode) {
        initializeUnixMode();
    } else {
        initializeStandardMode();
    }

    function initializeUnixMode() {
        // Unix Mode Initialization
        const terminalInput = document.getElementById('terminal-command');
        const terminalOutput = document.getElementById('terminal-output');

        terminalInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                const command = terminalInput.value.trim();
                terminalInput.value = '';
                processCommand(command);
            }
        });

        function processCommand(command) {
            fetch('/unix_command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `command=${encodeURIComponent(command)}`
            })
                .then(response => response.json())
                .then(data => {
                    if (data.exit) {
                        window.location.reload();
                    } else if (data.clear) {
                        terminalOutput.innerHTML = '';
                    } else if (data.output) {
                        const outputLine = document.createElement('div');
                        outputLine.textContent = data.output;
                        terminalOutput.appendChild(outputLine);
                        terminalOutput.scrollTop = terminalOutput.scrollHeight;
                    } else {
                        const outputLine = document.createElement('div');
                        outputLine.textContent = 'Unknown response from server.';
                        terminalOutput.appendChild(outputLine);
                        terminalOutput.scrollTop = terminalOutput.scrollHeight;
                    }
                })
                .catch(error => {
                    console.error('Error processing command:', error);
                    const outputLine = document.createElement('div');
                    outputLine.textContent = 'Error processing command.';
                    terminalOutput.appendChild(outputLine);
                    terminalOutput.scrollTop = terminalOutput.scrollHeight;
                });
        }
    }

    function initializeStandardMode() {
        // Elements for the normal interface
        const logForm = document.getElementById('log-form');
        const logInput = document.getElementById('log-input');
        const combinedLogContainer = document.getElementById('combined-log-container');
        const checkLogsButton = document.getElementById('check-logs-button');
        const returnLogButton = document.getElementById('return-log-button');
        const endSessionButton = document.getElementById('end-session-button');
        const terminatedGif = document.getElementById('terminated-gif');
        const paginationDiv = document.getElementById('pagination-div');
        const toolsButton = document.getElementById('tools-button');
        const toolsModal = document.getElementById('tools-modal');
        const closeModal = document.querySelector('.close');
        const sessionTitleElement = document.getElementById('session-title');
        const sessionInfoContainer = document.getElementById('session-info-container');
        const rollButton = document.getElementById('roll-button');
        const diceResult = document.getElementById('dice-result');
        const diceCountInput = document.getElementById('dice-count');

        // Log Form Submission
        if (logForm) {
            logForm.addEventListener('submit', function (event) {
                event.preventDefault();
                const logMessage = logInput.value.trim();
                if (!logMessage) {
                    alert('Log message cannot be empty.');
                    return;
                }

                // Send the log message to the server
                fetch('/log', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: `log_message=${encodeURIComponent(logMessage)}`
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.entry) {
                            logInput.value = '';
                            alert('Log entry added successfully.');
                        } else {
                            alert('Failed to add log entry.');
                        }
                    })
                    .catch(error => console.error('Error adding log entry:', error));
            });
        }

        // Check Logs Button
        if (checkLogsButton) {
            checkLogsButton.addEventListener('click', function () {
                fetch('/combined_log')
                    .then(response => response.json())
                    .then(data => {
                        if (data.sessions && data.sessions.length > 0) {
                            displayCombinedLogs(data.sessions);
                        } else {
                            alert('No logs available.');
                        }
                    })
                    .catch(error => console.error('Error fetching combined logs:', error));
            });
        }

        // Return to Log Button
        if (returnLogButton) {
            returnLogButton.addEventListener('click', function () {
                combinedLogContainer.style.display = 'none';
                returnLogButton.style.display = 'none';
                checkLogsButton.style.display = 'inline-block';
                logForm.style.display = 'flex';
                endSessionButton.style.display = 'inline-block';
                paginationDiv.style.display = 'none';
                sessionTitleElement.textContent = '';
                sessionInfoContainer.style.display = 'none';
            });
        }

        // End Session Button
        if (endSessionButton) {
            endSessionButton.addEventListener('click', function () {
                fetch('/end_session', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('Session ended successfully.');
                            // Optionally, redirect or refresh the page
                        } else {
                            alert('Failed to end session.');
                        }
                    })
                    .catch(error => console.error('Error ending session:', error));
            });
        }

        // Tools Button and Modal Logic
        if (toolsButton) {
            toolsButton.addEventListener('click', function () {
                toolsModal.style.display = 'block';
            });
        }

        if (closeModal) {
            closeModal.addEventListener('click', function () {
                toolsModal.style.display = 'none';
            });
        }

        // Close modal when clicking outside of it
        window.addEventListener('click', function (event) {
            if (event.target == toolsModal) {
                toolsModal.style.display = 'none';
            }
        });

        // Dice Roll Logic
        if (rollButton) {
            rollButton.addEventListener('click', function () {
                const diceCount = parseInt(diceCountInput.value);
                if (isNaN(diceCount) || diceCount <= 0) {
                    diceResult.textContent = 'Please enter a valid number of dice.';
                    return;
                }

                const results = [];
                let successes = 0;
                let ones = 0;
                for (let i = 0; i < diceCount; i++) {
                    const roll = Math.floor(Math.random() * 6) + 1;
                    results.push(roll);
                    if (roll === 5 || roll === 6) {
                        successes++;
                    }
                    if (roll === 1) {
                        ones++;
                    }
                }

                let outcome = '';
                if (successes > 0) {
                    outcome = `Successes: ${successes}`;
                } else {
                    outcome = 'Failure';
                }

                // Check for Glitch or Critical Glitch
                if (ones > diceCount / 2) {
                    if (successes === 0) {
                        outcome += ' (Critical Glitch)';
                    } else {
                        outcome += ' (Glitch)';
                    }
                }

                diceResult.textContent = `You rolled: ${results.join(', ')}\n${outcome}`;
            });
        }

        // Function to display combined logs with pagination
        function displayCombinedLogs(sessions) {
            combinedLogContainer.innerHTML = '';
            combinedLogContainer.style.display = 'block';
            logForm.style.display = 'none';
            endSessionButton.style.display = 'none';
            checkLogsButton.style.display = 'none';
            returnLogButton.style.display = 'inline-block';
            sessionInfoContainer.style.display = 'block';

            // Flatten logs into a single array
            let allLogs = [];
            sessions.forEach(session => {
                session.logs.forEach(log => {
                    allLogs.push({
                        sessionTitle: session.sessionTitle,
                        sessionTimestamp: session.sessionTimestamp,
                        timestamp: log.timestamp,
                        message: log.message,
                        id: log.id
                    });
                });
            });

            // Reverse the logs to show the latest ones first
            allLogs.reverse();

            // Pagination variables
            const itemsPerPage = 10;
            let currentPage = 1;
            const totalPages = Math.ceil(allLogs.length / itemsPerPage);

            function renderPage(page) {
                combinedLogContainer.innerHTML = '';
                const start = (page - 1) * itemsPerPage;
                const end = start + itemsPerPage;
                const logsToDisplay = allLogs.slice(start, end);

                logsToDisplay.forEach(log => {
                    const logEntry = document.createElement('div');
                    logEntry.classList.add('log-entry');

                    const logContent = document.createElement('div');
                    logContent.classList.add('log-message');
                    logContent.textContent = `[${log.timestamp}] ${log.message}`;

                    // Edit Button
                    const editButton = document.createElement('button');
                    editButton.classList.add('edit-button');
                    editButton.title = 'Edit Log';
                    editButton.addEventListener('click', () => {
                        const newMessage = prompt('Enter new log message:', log.message);
                        if (newMessage !== null) {
                            editLog(log.id, newMessage);
                        }
                    });

                    // Append elements
                    logEntry.appendChild(logContent);
                    logEntry.appendChild(editButton);
                    combinedLogContainer.appendChild(logEntry);

                    // Separator
                    const separator = document.createElement('div');
                    separator.classList.add('separator');
                    combinedLogContainer.appendChild(separator);
                });

                // Display session title and timestamp at the bottom
                if (logsToDisplay.length > 0) {
                    const lastLog = logsToDisplay[logsToDisplay.length - 1];
                    sessionTitleElement.textContent = `${lastLog.sessionTitle} - ${lastLog.sessionTimestamp}`;
                }

                renderPagination();
            }

            function renderPagination() {
                paginationDiv.innerHTML = '';
                paginationDiv.style.display = 'flex';

                for (let i = 1; i <= totalPages; i++) {
                    const pageButton = document.createElement('button');
                    pageButton.textContent = `[${i}]`;
                    pageButton.classList.add('pagination-button');
                    if (i === currentPage) {
                        pageButton.disabled = true;
                        pageButton.style.opacity = '0.6';
                    }
                    pageButton.addEventListener('click', () => {
                        currentPage = i;
                        renderPage(currentPage);
                    });
                    paginationDiv.appendChild(pageButton);
                }
            }

            function editLog(logId, newMessage) {
                // Send edit request based on UUID
                fetch('/edit_log', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `log_id=${encodeURIComponent(logId)}&new_message=${encodeURIComponent(newMessage)}`
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert(`Log updated successfully.`);
                            // Refresh the logs
                            fetch('/combined_log')
                                .then(response => response.json())
                                .then(data => {
                                    displayCombinedLogs(data.sessions);
                                })
                                .catch(error => console.error('Error fetching combined logs:', error));
                        } else {
                            alert(`Failed to update log: ${data.error}`);
                        }
                    })
                    .catch(error => console.error('Error updating log:', error));
            }

            // Initial render
            renderPage(currentPage);
        }
    }
});
