// static/js/script.js

// DOM bereit
document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap Tooltips initialisieren
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Formularvalidierung aktivieren
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Ausgabenerfassung - Dynamisches Formular
    const categorySelect = document.getElementById('id_category');
    const otherCategoryField = document.getElementById('other_category_group');

    if (categorySelect && otherCategoryField) {
        // Verstecke das "Andere" Feld initial
        otherCategoryField.style.display = 'none';

        categorySelect.addEventListener('change', function() {
            // Wenn "Andere" ausgewählt ist
            if (this.value === 'other') {
                otherCategoryField.style.display = 'block';
            } else {
                otherCategoryField.style.display = 'none';
            }
        });
    }

    // Belegscannen - Bild-Vorschau
    const receiptInput = document.getElementById('id_receipt_image');
    const receiptPreview = document.getElementById('receipt_preview');

    if (receiptInput && receiptPreview) {
        receiptInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();

                reader.onload = function(e) {
                    receiptPreview.src = e.target.result;
                    receiptPreview.style.display = 'block';
                };

                reader.readAsDataURL(this.files[0]);
            }
        });
    }

    // Budget-Formulare - Dynamisches Hinzufügen von Kategorien
    const addCategoryBtn = document.getElementById('add_category_btn');
    const categoryContainer = document.getElementById('category_formset');

    if (addCategoryBtn && categoryContainer) {
        addCategoryBtn.addEventListener('click', function() {
            const forms = categoryContainer.getElementsByClassName('category-form');
            const formNum = forms.length;
            const totalForms = document.getElementById('id_budgetcategory_set-TOTAL_FORMS');

            // Klone das letzte Formular
            const newForm = forms[forms.length - 1].cloneNode(true);

            // Aktualisiere IDs und Namen
            let formRegex = RegExp(`budgetcategory_set-(\\d){1}-`,'g');
            newForm.innerHTML = newForm.innerHTML.replace(formRegex, `budgetcategory_set-${formNum}-`);

            // Setze Werte zurück
            const inputs = newForm.querySelectorAll('input, select');
            inputs.forEach(input => {
                if (input.type === 'text' || input.type === 'number') {
                    input.value = '';
                }
            });

            // Füge das neue Formular hinzu
            categoryContainer.appendChild(newForm);

            // Aktualisiere den Zähler
            totalForms.value = formNum + 1;
        });
    }

    // Sparziel-Fortschritt animieren
    const progressBars = document.querySelectorAll('.animate-progress');

    if (progressBars.length > 0) {
        progressBars.forEach(progress => {
            const targetWidth = progress.getAttribute('data-progress') + '%';
            setTimeout(() => {
                progress.style.width = targetWidth;
            }, 300);
        });
    }

    // Ausgabenverlauf - Diagramm
    const expenseChartCanvas = document.getElementById('expenseChart');

    if (expenseChartCanvas) {
        // Daten aus data-Attribut extrahieren
        const chartData = JSON.parse(expenseChartCanvas.getAttribute('data-chart'));

        // Chart.js Diagramm erstellen
        new Chart(expenseChartCanvas, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Ausgaben',
                    data: chartData.values,
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    borderColor: 'rgba(13, 110, 253, 1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.raw + ' CHF';
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value + ' CHF';
                            }
                        }
                    }
                }
            }
        });
    }

    // Kategorien-Verteilung - Ringdiagramm
    const categoryChartCanvas = document.getElementById('categoryChart');

    if (categoryChartCanvas) {
        // Daten aus data-Attribut extrahieren
        const chartData = JSON.parse(categoryChartCanvas.getAttribute('data-chart'));

        // Chart.js Diagramm erstellen
        new Chart(categoryChartCanvas, {
            type: 'doughnut',
            data: {
                labels: chartData.labels,
                datasets: [{
                    data: chartData.values,
                    backgroundColor: [
                        'rgba(13, 110, 253, 0.7)',
                        'rgba(25, 135, 84, 0.7)',
                        'rgba(220, 53, 69, 0.7)',
                        'rgba(255, 193, 7, 0.7)',
                        'rgba(13, 202, 240, 0.7)',
                        'rgba(111, 66, 193, 0.7)',
                        'rgba(214, 51, 132, 0.7)',
                        'rgba(108, 117, 125, 0.7)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw + ' CHF';
                                const percentage = Math.round(context.raw / chartData.total * 100) + '%';
                                return `${label}: ${value} (${percentage})`;
                            }
                        }
                    }
                }
            }
        });
    }

    // Dark Mode Toggle
    const darkModeToggle = document.getElementById('darkModeToggle');

    if (darkModeToggle) {
        // Prüfe gespeicherte Einstellung
        const darkMode = localStorage.getItem('darkMode') === 'true';

        // Setze initialen Zustand
        if (darkMode) {
            document.body.classList.add('dark-mode');
            darkModeToggle.checked = true;
        }

        // Toggle Event
        darkModeToggle.addEventListener('change', function() {
            if (this.checked) {
                document.body.classList.add('dark-mode');
                localStorage.setItem('darkMode', 'true');
            } else {
                document.body.classList.remove('dark-mode');
                localStorage.setItem('darkMode', 'false');
            }
        });
    }
});