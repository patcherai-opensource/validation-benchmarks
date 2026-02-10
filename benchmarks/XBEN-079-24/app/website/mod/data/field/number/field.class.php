<?php
class data_field_number {
    public $type = 'number';
    public $name = 'Number Input';
    public $description = 'A numeric input field';
    
    public function render() {
        return '<input type="number" class="form-control" />';
    }
    
    public function get_info() {
        return array(
            'type' => $this->type,
            'name' => $this->name,
            'description' => $this->description
        );
    }
}
?>
