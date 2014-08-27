
        
<h1>Apresentação</h1>
Tweet Collector é um script que utiliza a Twitter Streaming API para espacializar os Tweets de acordo com um termo específico de busca.
Para cada termo um FILEGDB é criado com o nome do termo especificado.<br/><br/>
Foi desenvolvido em Python 2.7 e utiliza recursos da biblioteca ArcPy fornecida pela suíte de aplicativos desktop do ArcGIS 10.2.
Utiliza a arquitetura multi-thread para uma otimização dos recursos de máquina.<br/><br/>
O pacote do script Tweet Collector contém os seguintes itens listados abaixo. <br/><br/>
Todos os itens são obrigatórios para a execução do script.<br/><br/>
<ul>
    <li><strong>oauth2 (pasta library)</strong></li>
    É uma biblioteca do Python necessária para a autenticação segura no Twitter via oauth.<br/><br/>
    <li><strong>twitter.gdb (file GDB)</strong></li>
    É o ‘banco de dados’ modelo do script. Dentro dele existe uma Feature Class Tweet que está completamente vazia. Cópias desse fileGDB serão realizadas para cada novo termo de pesquisa inserido.<br/>
    Este banco nunca deve ser alterado, ou ter registros inseridos.<br/><br/>
    <li><strong>config.xml (arquivo.xml configuração)</strong></li>
    É o arquivo de configuração do script. Nele colocamos os termos que serão monitorados, e as chaves de autenticação de cada termo. Veremos ambos no seção Configuração.<br/><br/>
    <li><strong>tweet-collector (script)</strong></li>
    É o script propriamente dito, que contém toda a lógica de coleta e armazenamento dos Tweets. Após todas as configurações necessárias serem realizadas, é esse o arquivo que deve ser executado.
</ul>

<h2>LEIA-ME para mais informações</h2>