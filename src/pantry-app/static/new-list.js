$(window).ready(function() {
    $("#add-button").click(function() {
        let itemNum = parseInt($('input[name="num-items"]')[0].value) + 1;
        let newItem = $(`#item-${itemNum - 1}`).clone();
        $(`#item-${itemNum - 1}`).after(newItem);

        newItem.attr("id", `item-${itemNum}`);
        newItem.find(".form-group-title").html(`Item #${itemNum}`);
        newItem.find(`label[for="item-name-${itemNum - 1}"]`).first().attr(
            'for',
            `item-name-${itemNum}`);
        newItem.find(`input[name="item-name-${itemNum - 1}"]`).first().attr(
            'name',
            `item-name-${itemNum}`);
        newItem.find(`input[name="item-name-${itemNum - 1}"]`).first().html(' ');

        $('input[name="num-items"]')[0].value = itemNum.toString();
    });

    $("#remove-button").click(function() {
        let itemNum = parseInt($('input[name="num-items"]')[0].value) - 1;

        if (itemNum <= 0) {
            return;
        }

        let targetItem = $(`#item-${itemNum + 1}`);
        targetItem.remove();

        $('input[name="num-items"]')[0].value = itemNum.toString();
    });
});