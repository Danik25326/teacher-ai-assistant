document.addEventListener('DOMContentLoaded', function() {
    const bookSelect = document.getElementById('book_id');
    const topicInput = document.getElementById('topic');
    const topicsDatalist = document.getElementById('topics');

    bookSelect.addEventListener('change', function() {
        const bookId = this.value;
        fetch(`/api/book/${bookId}/topics`)
            .then(response => response.json())
            .then(data => {
                topicsDatalist.innerHTML = '';
                data.topics.forEach(topic => {
                    const option = document.createElement('option');
                    option.value = topic;
                    topicsDatalist.appendChild(option);
                });
            });
    });
});
