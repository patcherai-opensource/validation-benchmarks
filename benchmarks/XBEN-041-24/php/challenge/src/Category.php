<?php

namespace phpMyFAQ\Category;

class Category
{
    private string $dataFile;

    public function __construct(string $dataFile = '/var/www/html/data/categories.json')
    {
        $this->dataFile = $dataFile;
    }

    public function getAll(): array
    {
        if (!file_exists($this->dataFile)) {
            return [];
        }
        $data = json_decode(file_get_contents($this->dataFile), true);
        return is_array($data) ? $data : [];
    }

    public function getById(int $id): ?array
    {
        $categories = $this->getAll();
        foreach ($categories as $cat) {
            if ($cat['id'] === $id) {
                return $cat;
            }
        }
        return null;
    }

    public function add(string $name, string $description, string $lang): int
    {
        $categories = $this->getAll();
        $maxId = 0;
        foreach ($categories as $cat) {
            if ($cat['id'] > $maxId) {
                $maxId = $cat['id'];
            }
        }
        $newId = $maxId + 1;
        $categories[] = [
            'id' => $newId,
            'name' => $name,
            'description' => $description,
            'lang' => $lang,
            'created' => date('Y-m-d H:i:s'),
            'active' => true
        ];
        file_put_contents($this->dataFile, json_encode($categories, JSON_PRETTY_PRINT));
        return $newId;
    }

    public function update(int $id, string $name, string $description, string $lang): bool
    {
        $categories = $this->getAll();
        foreach ($categories as &$cat) {
            if ($cat['id'] === $id) {
                $cat['name'] = $name;
                $cat['description'] = $description;
                $cat['lang'] = $lang;
                $cat['updated'] = date('Y-m-d H:i:s');
                file_put_contents($this->dataFile, json_encode($categories, JSON_PRETTY_PRINT));
                return true;
            }
        }
        return false;
    }

    public function delete(int $id): bool
    {
        $categories = $this->getAll();
        $filtered = array_filter($categories, fn($cat) => $cat['id'] !== $id);
        if (count($filtered) < count($categories)) {
            file_put_contents($this->dataFile, json_encode(array_values($filtered), JSON_PRETTY_PRINT));
            return true;
        }
        return false;
    }
}
