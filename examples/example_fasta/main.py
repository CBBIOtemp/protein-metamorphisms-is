from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from protein_data_handler.helpers.config.yaml import read_yaml_config
from protein_data_handler.helpers.database.database import create_session
from protein_data_handler.fasta import FastaHandler  # Asegúrate de ajustar la ruta de importación
from protein_data_handler.models.uniprot import Base, PDBReference


def main():
    config = read_yaml_config("./config.yaml")
    DATABASE_URI = \
        (f"postgresql+psycopg2://{config['DB_USERNAME']}:"
         f"{config['DB_PASSWORD']}"
         f"@{config['DB_HOST']}:"
         f"{config['DB_PORT']}/"
         f"{config['DB_NAME']}")
    engine = create_engine(DATABASE_URI)

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    query = session.query(PDBReference).filter(PDBReference.resolution < config.get("resolution_threshold", 2.5)).all()
    pdb_ids = [pdb_ref.pdb_id for pdb_ref in query]
    # Inicializa FastaHandler
    fasta_downloader = FastaHandler(session, config['data_dir'], config['output_dir'])

    # Descarga los archivos FASTA
    fasta_downloader.download_fastas(pdb_ids[:-500], config['max_workers'])

    fasta_downloader.merge_fastas(pdb_ids,config['merge_name'])


if __name__ == "__main__":
    main()