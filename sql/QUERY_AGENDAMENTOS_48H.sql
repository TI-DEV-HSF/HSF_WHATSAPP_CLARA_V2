--21/11/2024
--@PLima
-- RELATORIO 1803 - HSF- Agenda psiquiatria X psicologia - Excel

select
    EXTRACT(YEAR FROM a.dt_agenda)                  ANO,
    EXTRACT(MONTH FROM a.dt_agenda)                 MES,
    EXTRACT(DAY FROM a.dt_agenda)                   DIA,
    A.NR_SEQUENCIA                                  NR_SEQ_AGENDA,
    obter_cpf_pessoa_fisica(A.CD_PESSOA_FISICA)     NR_CPF,
    a.ie_classif_agenda                             CD_TIPO_AGENDA,
    'CLARA'                                         NM_USUARIO,                            
    to_char(a.dt_agenda, 'dd/mm/yyyy hh24:mi')      DT_AGENDA,
    A.CD_PESSOA_FISICA                              CD_PESSOA_FISICA,
    obter_cpf_pessoa_fisica(A.CD_PESSOA_FISICA)     CPF,
    TRIM(REPLACE(REPLACE(INITCAP(A.NM_PACIENTE), '1vez',''),'1 Vez','')) NM_PACIENTE,
    a.ie_status_agenda                              IE_STATUS_AGENDA,
    INITCAP(a.ds_status_agenda)                     DS_STATUS_AGENDA,
    SUBSTR(
            REPLACE(REPLACE(REPLACE(A.NR_TELEFONE,'M:',''),'(',''),')','')
        ,
        1, 
        12
        )                                           TELEFONE,
    INITCAP(
        OBTER_CLASSIF_AGENDA_CONSULTA(
            a.ie_classif_agenda))                   DS_CLASSIF_AGENDA,
    b.cd_especialidade                              CD_ESPECIALIDADE,
    INITCAP(
        decode(
            B.cd_especialidade, 
            null, obter_especialidades_medico(B.cd_pessoa_fisica), 
            (
                select 
                max(ds_especialidade) 
                from especialidade_medica 
                where cd_especialidade = B.cd_especialidade)
                )
            )                                       DS_ESPECIALIDADE,
    b.cd_agenda                                     CD_AGENDA,
    INITCAP(REPLACE(b.ds_agenda,'(Nova)',''))       DS_AGENDA,
    --A.CD_MEDICO_REQ,                            
    -- Se NM_MEDICO_RESP for NULL, usa NM_PROFISSIONAL_AGENDA
    INITCAP(
        COALESCE(
            obter_nome_medico(a.CD_MEDICO_REQ,'PS'), 
            obter_nome_medico(b.CD_PESSOA_FISICA,'PS')
        )
    )                                               NM_MEDICO_RESP
from 	Agenda_Consulta_v a
left join Agenda b on (a.cd_agenda = b.cd_agenda)
left join Convenio E on (E.CD_CONVENIO = A.CD_CONVENIO)
where 	trunc(a.dt_agenda) = trunc(SYSDATE+2)
AND a.IE_STATUS_AGENDA <> 'L'
AND a.IE_STATUS_AGENDA <> 'C'
AND a.IE_STATUS_AGENDA <> 'B'
AND a.IE_STATUS_AGENDA <> 'II'
AND A.CD_PESSOA_FISICA IS NOT NULL
AND A.NR_TELEFONE IS NOT NULL
--AND b.cd_agenda IN (110,111, 46, 47, 48, 50, 42,228,56,266,54,542,211,456,559) 

AND( 
        b.cd_agenda IN (46,33,69,15,75,71,6,9,4,24,28,56,63,2,21,72,8) 
    
    or
        INITCAP(
               decode(
                   B.cd_especialidade, 
                   null, obter_especialidades_medico(B.cd_pessoa_fisica), 
                   (
                       select 
                       max(ds_especialidade) 
                       from especialidade_medica 
                       where cd_especialidade = B.cd_especialidade)
                       )
                   ) IN (
                           'Psicologia',
                           'Psiquiatria',
                           'Angiologia',
                           'Arritmologia',
                           'Bucomaxilo',
                           'Cardiologia',
                           'Craniomaxilofacial',
                           'Cirurgia Bariátria',
                           'Clínica da Dor',
                           'Clínica médica',
                           'Cirurgia Toracica',
                           'Cirurgia Geral',
                           'Oncologia',
                           'Cirurgia Geral',
                           'Cirurgia Plástica',
                           'Hematologia',
                           'Mastologia',
                           'Odontologia',
                           'Ortopedia',
                           'Pneumologia',
                           'Proctologia',
                           'Reumatologia'
                        )
    --Regras para retornar pela agenda do medico usando o nome do mesmo
    or UPPER(
            COALESCE(
                obter_nome_medico(a.CD_MEDICO_REQ,'PS'), 
                obter_nome_medico(b.CD_PESSOA_FISICA,'PS')
            )
        ) like UPPER('%Sylvio%')

    or UPPER(
        COALESCE(
            obter_nome_medico(a.CD_MEDICO_REQ,'PS'), 
            obter_nome_medico(b.CD_PESSOA_FISICA,'PS')
        )
    ) like UPPER('%Aurelio%Bottino%')
    or UPPER(
            COALESCE(
                obter_nome_medico(a.CD_MEDICO_REQ,'PS'), 
                obter_nome_medico(b.CD_PESSOA_FISICA,'PS')
            )
        ) like UPPER('%Bernardo%')
    or UPPER(
            COALESCE(
                obter_nome_medico(a.CD_MEDICO_REQ,'PS'), 
                obter_nome_medico(b.CD_PESSOA_FISICA,'PS')
            )
        ) like UPPER('%Alexandre%Amaral%')
    or UPPER(
            COALESCE(
                obter_nome_medico(a.CD_MEDICO_REQ,'PS'), 
                obter_nome_medico(b.CD_PESSOA_FISICA,'PS')
            )
        ) like UPPER('%Lui%gio%')
    or UPPER(
            COALESCE(
                obter_nome_medico(a.CD_MEDICO_REQ,'PS'), 
                obter_nome_medico(b.CD_PESSOA_FISICA,'PS')
            )
        ) like UPPER('%Filipe%Calado%')
    or UPPER(
            COALESCE(
                obter_nome_medico(a.CD_MEDICO_REQ,'PS'), 
                obter_nome_medico(b.CD_PESSOA_FISICA,'PS')
            )
        ) like UPPER('%Willian%Wilmer%')


    )

and COALESCE(
            obter_nome_medico(a.CD_MEDICO_REQ,'PS'), 
            obter_nome_medico(b.CD_PESSOA_FISICA,'PS')
        ) is not null

-- Tira a iole, ana carolina, e larissa
and UPPER(
        COALESCE(
            obter_nome_medico(a.CD_MEDICO_REQ,'PS'), 
            obter_nome_medico(b.CD_PESSOA_FISICA,'PS')
        )
    ) NOT like ('%IOLE%')
and UPPER(
        COALESCE(
            obter_nome_medico(a.CD_MEDICO_REQ,'PS'), 
            obter_nome_medico(b.CD_PESSOA_FISICA,'PS')
        )
    ) NOT like UPPER('%ana%carolina%')
and UPPER(
        COALESCE(
            obter_nome_medico(a.CD_MEDICO_REQ,'PS'), 
            obter_nome_medico(b.CD_PESSOA_FISICA,'PS')
        )
    ) NOT like UPPER('%larissa%lima%')    

order by 	8, 20 , 11
--FETCH FIRST 1 ROWS ONLY