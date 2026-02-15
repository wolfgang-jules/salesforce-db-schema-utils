SELECT
  EntityDefinitionId,
  QualifiedApiName,
  Label,
  DataType,
  ValueTypeId,
  Description,
  NamespacePrefix,
  PublisherId
FROM
  FieldDefinition
WHERE
  EntityDefinitionId = '{table_name}'